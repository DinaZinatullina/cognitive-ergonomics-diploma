// ============================================================
// Система когнитивной эргономики — клиентская логика (SCADA)
// ============================================================

(function () {
    'use strict';

    // CSRF-токен из data-атрибута body
    const csrfToken = document.body.dataset.csrfToken;

    // Состояние системы
    const state = {
        lastActionAt: Date.now(),
    };

    // ============================================================
    // Отправка события на сервер
    // ============================================================
    function sendEvent(eventType, target, reactionTimeMs) {
        const payload = {
            event_type: eventType,
            target: target || '',
            reaction_time_ms: reactionTimeMs || null,
        };

        fetch('/api/event/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(payload),
        }).catch(function (err) {
            console.warn('Не удалось отправить событие:', err);
        });
    }

    // ============================================================
    // Опрос состояния установки и обновление мнемосхемы
    // ============================================================
    function fetchEquipmentStatus() {
        fetch('/api/equipment/')
            .then(r => r.json())
            .then(data => {
                // 1. Находим элементы
                const tempEl = document.getElementById('val-temp');
                const pressureEl = document.getElementById('val-pressure');
                const levelEl = document.getElementById('mnemonic-level');
                const tempMnemonicEl = document.getElementById('mnemonic-temp');
                const tankFluidEl = document.getElementById('tank-fluid');
                const alarmEl = document.getElementById('alarm-panel');
                const reactorEl = document.getElementById('reactor-icon');
                const statusEl = document.getElementById('system-status');
                const pumpEl = document.getElementById('pump-icon');

                // Если элементов нет (мы на другой странице), выходим
                if (!tempEl || !levelEl) return;

                // 2. Обновляем цифры
                tempEl.textContent = data.temperature.toFixed(1);
                pressureEl.textContent = data.pressure.toFixed(2);
                levelEl.textContent = Math.round(data.tank_level) + '%';
                tempMnemonicEl.textContent = Math.round(data.temperature) + '°C';

                // 3. Двигаем воду в баке и полоски
                tankFluidEl.style.height = data.tank_level + '%';
                
                const tempPercent = Math.min((data.temperature / 120) * 100, 100);
                document.getElementById('bar-temp').style.width = tempPercent + '%';
                
                const pressPercent = Math.min((data.pressure / 4.0) * 100, 100);
                document.getElementById('bar-pressure').style.width = pressPercent + '%';

                // 5. Обработка аварий
                let isAlarm = false;

                if (data.is_temperature_critical) {
                    tempEl.classList.add('danger-text');
                    document.getElementById('bar-temp').classList.add('danger-bar');
                    reactorEl.classList.add('danger');
                    isAlarm = true;
                } else {
                    tempEl.classList.remove('danger-text');
                    document.getElementById('bar-temp').classList.remove('danger-bar');
                    reactorEl.classList.remove('danger');
                }

                if (data.is_pressure_critical) {
                    pressureEl.classList.add('danger-text');
                    document.getElementById('bar-pressure').classList.add('danger-bar');
                    isAlarm = true;
                } else {
                    pressureEl.classList.remove('danger-text');
                    document.getElementById('bar-pressure').classList.remove('danger-bar');
                }
                                // Управление потоком в трубе
                const pipeFlow = document.getElementById('pipe-flow');
                if (pipeFlow) {
                    // Если насос должен работать (нет аварии и есть вода) — показываем поток
                    if (data.is_pump_working) {
                        pipeFlow.style.display = 'block';
                    } else {
                        pipeFlow.style.display = 'none';
                    }
                }

                // 6. Статус и предупреждения
                if (isAlarm) {
                    // КРИТИЧЕСКАЯ АВАРИЯ
                    alarmEl.style.display = 'flex';
                    statusEl.innerHTML = '<span class="status-dot" style="background:#ef4444; box-shadow:0 0 8px #ef4444;"></span> АВАРИЯ';
                    statusEl.style.color = '#ef4444';
                    reactorEl.style.borderColor = '#ef4444'; // Красная рамка
                    
                    if (!window._alarmSent) {
                        sendEvent('alert', 'критическое_отклонение', null);
                        addLog('Критическое отклонение параметров!', 'danger');
                        window._alarmSent = true;
                    }
                } else if (data.is_predictive_warning) {
                    // ПРЕДИКТИВНОЕ ПРЕДУПРЕЖДЕНИЕ (рост параметров)
                    alarmEl.style.display = 'none';
                    statusEl.innerHTML = '<span class="status-dot" style="background:#fbbf24; box-shadow:0 0 8px #fbbf24;"></span> ВНИМАНИЕ: РОСТ ПАРАМЕТРОВ';
                    reactorEl.style.borderColor = '#fbbf24';
                    window._alarmSent = false;
                } else {
                    // НОРМА
                    alarmEl.style.display = 'none';
                    statusEl.innerHTML = '<span class="status-dot"></span> СИСТЕМА В НОРМЕ';
                    statusEl.style.color = '#4ade80';
                    reactorEl.style.borderColor = '#475569';
                    window._alarmSent = false;
                }

                // 7. Логика авто-защиты
                if (data.is_auto_protected) {
                    if (!window._autoProtectSent) {
                        addLog('СИСТЕМА ВЗЯЛА УПРАВЛЕНИЕ: Аварийный сброс!', 'danger');
                        sendEvent('system_action', 'auto_protection', null);
                        window._autoProtectSent = true;
                    }
                } else {
                    window._autoProtectSent = false;
                }
            })
            .catch(err => console.warn('Ошибка получения данных установки:', err));
    }

    // Функция для добавления записи в журнал
    function addLog(text, type) {
        const logContainer = document.getElementById('scada-log');
        if (!logContainer) return;
        
        const now = new Date();
        const timeStr = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
        
        const entry = document.createElement('div');
        entry.className = 'log-entry ' + (type || 'info');
        entry.textContent = `[${timeStr}] ${text}`;
        
        logContainer.prepend(entry);
    }

    // ============================================================
    // Обработка кнопок управления
    // ============================================================
    function setupControlButtons() {
        const controlButtons = document.querySelectorAll('.control-buttons .scada-btn');
        
        controlButtons.forEach(function (button) {
            button.addEventListener('click', function () {
                const action = button.dataset.action;
                const reactionTime = Date.now() - state.lastActionAt;
                
                sendEvent('click', 'control_' + action, reactionTime);
                
                fetch('/api/equipment/control/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ action: action }),
                })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        addLog('Команда: ' + button.textContent.trim(), 'info');
                    }
                })
                .catch(err => console.warn('Ошибка управления:', err));

                state.lastActionAt = Date.now();
            });
        });
    }

    // ============================================================
    // Адаптация интерфейса
    // ============================================================
    function fetchAdaptation() {
        fetch('/api/adaptation/')
            .then(r => r.json())
            .then(data => {
                if (data.actions && data.actions.length > 0) {
                    data.actions.forEach(applyAdaptationAction);
                }
            })
            .catch(err => console.warn('Не удалось получить адаптацию:', err));
    }

    function applyAdaptationAction(action) {
        if (action === 'simplify_ui') {
            document.body.classList.add('simplified');
        } else if (action === 'show_hint') {
            showHint('Вы часто ошибаетесь. Проверьте, запущена ли система, прежде чем её останавливать.');
        } else if (action === 'increase_font') {
            document.body.classList.add('large-font');
        }
    }

    function showHint(text) {
        const existing = document.querySelector('.hint-bar');
        if (existing) existing.remove();

        const hint = document.createElement('div');
        hint.className = 'hint-bar';
        hint.textContent = text;
        document.body.insertBefore(hint, document.body.firstChild);

        setTimeout(() => hint.remove(), 15000);
    }

    // ============================================================
    // Запуск
    // ============================================================
    document.addEventListener('DOMContentLoaded', function () {
        if (document.getElementById('val-temp')) {
            setInterval(fetchEquipmentStatus, 2000);
            fetchEquipmentStatus();
            setupControlButtons();
            setInterval(fetchAdaptation, 5000);
        }

        document.addEventListener('click', function () {
            state.lastActionAt = Date.now();
        });
        
        setInterval(function () {
            const idleSeconds = Math.floor((Date.now() - state.lastActionAt) / 1000);
            if (idleSeconds >= 30 && idleSeconds % 30 === 0) {
                sendEvent('idle', 'idle_' + idleSeconds + 's', null);
            }
        }, 1000);
    });

})();