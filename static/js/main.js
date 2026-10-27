// ============================================================
// Система когнитивной эргономики — клиентская логика
// ============================================================

(function () {
    'use strict';

    // CSRF-токен из data-атрибута body
    const csrfToken = document.body.dataset.csrfToken;

    // Состояние системы (для определения ошибок)
    const state = {
        isRunning: false,
        sessionStart: Date.now(),
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
    // Кнопки действий
    // ============================================================
    const buttons = document.querySelectorAll('.actions button');

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            const action = button.dataset.action || button.textContent.trim();
            const reactionTime = Date.now() - state.lastActionAt;

            // Проверка на ошибку:
            // если нажали "Остановить" или "Перезапустить",
            // а система не запущена — это ошибка оператора
            if ((action === 'stop' || action === 'restart') && !state.isRunning) {
                sendEvent('error', 'попытка_' + action + '_без_запуска', reactionTime);
                state.lastActionAt = Date.now();
                return;
            }

            // Обычный клик
            sendEvent('click', action, reactionTime);
            state.lastActionAt = Date.now();

            // Меняем состояние системы
            if (action === 'start') {
                state.isRunning = true;
            } else if (action === 'stop') {
                state.isRunning = false;
            }
        });
    });

    // ============================================================
    // Просмотр панелей (view)
    // Оператор навёл мышь на панель и задержался больше 1 секунды
    // ============================================================
    const panels = document.querySelectorAll('.panel');

    panels.forEach(function (panel) {
        let hoverStart = null;
        let hoverTimer = null;

        panel.addEventListener('mouseenter', function () {
            hoverStart = Date.now();
            hoverTimer = setTimeout(function () {
                const title = panel.querySelector('h2');
                const target = title ? title.textContent.trim() : 'panel';
                sendEvent('view', target, null);
            }, 1000); // через 1 секунду просмотра
        });

        panel.addEventListener('mouseleave', function () {
            if (hoverTimer) {
                clearTimeout(hoverTimer);
                hoverTimer = null;
            }
            hoverStart = null;
        });
    });

    // ============================================================
    // Idle-событие: если оператор ничего не делает 30 секунд
    // ============================================================
    setInterval(function () {
        const idleSeconds = Math.floor((Date.now() - state.lastActionAt) / 1000);
        if (idleSeconds >= 30 && idleSeconds % 30 === 0) {
            sendEvent('idle', 'idle_' + idleSeconds + 's', null);
        }
    }, 1000);

    // Обновляем lastActionAt при любом клике на странице
    document.addEventListener('click', function () {
        state.lastActionAt = Date.now();
    });

        // ============================================================
    // Получение и применение правил адаптации
    // ============================================================
    function fetchAdaptation() {
        fetch('/api/adaptation/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken,
            },
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.actions && data.actions.length > 0) {
                    data.actions.forEach(function (action) {
                        applyAdaptationAction(action);
                    });
                }
            })
            .catch(function (err) {
                console.warn('Не удалось получить адаптацию:', err);
            });
    }

    // Применение конкретного действия к интерфейсу
    function applyAdaptationAction(action) {
        if (action === 'simplify_ui') {
            document.body.classList.add('simplified');
        } else if (action === 'show_hint') {
            showHint('Вы часто ошибаетесь. Проверьте, запущена ли система, прежде чем её останавливать.');
        } else if (action === 'increase_font') {
            document.body.classList.add('large-font');
        }
    }

    // Показ подсказки сверху страницы
    function showHint(text) {
        // Удаляем предыдущую подсказку, если она есть
        const existing = document.querySelector('.hint-bar');
        if (existing) {
            existing.remove();
        }

        const hint = document.createElement('div');
        hint.className = 'hint-bar';
        hint.textContent = text;
        document.body.insertBefore(hint, document.body.firstChild);

        // Убираем через 15 секунд
        setTimeout(function () {
            hint.remove();
        }, 15000);
    }

    // Опрашиваем сервер каждые 5 секунд
    setInterval(fetchAdaptation, 5000);

        // ============================================================
    // Опрос состояния установки
    // ============================================================
    function fetchEquipmentStatus() {
        fetch('/api/equipment/', {
            method: 'GET',
        })
            .then(r => r.json())
            .then(data => {
                // Обновляем цифры на экране
                const tempEl = document.getElementById('val-temp');
                const pressureEl = document.getElementById('val-pressure');
                const levelEl = document.getElementById('val-level');
                const alarmEl = document.getElementById('alarm-panel');

                if (!tempEl) return; // Если мы не на странице оператора

                tempEl.textContent = data.temperature + ' °C';
                pressureEl.textContent = data.pressure + ' атм';
                levelEl.textContent = data.tank_level + ' %';

                // Подсветка критических значений
                if (data.is_temperature_critical) {
                    tempEl.classList.add('text-danger');
                } else {
                    tempEl.classList.remove('text-danger');
                }

                if (data.is_pressure_critical) {
                    pressureEl.classList.add('text-danger');
                } else {
                    pressureEl.classList.remove('text-danger');
                }

                // Показ аварийного баннера
                if (data.is_temperature_critical || data.is_pressure_critical) {
                    alarmEl.style.display = 'block';
                    
                    // Отправляем событие об аварии, чтобы это влияло на когнитивную нагрузку
                    if (!window._alarmSent) {
                        sendEvent('alert', 'критическое_отклонение', null);
                        window._alarmSent = true;
                    }
                } else {
                    alarmEl.style.display = 'none';
                    window._alarmSent = false;
                }
            })
            .catch(err => console.warn('Ошибка получения данных установки:', err));
    }

    // Запускаем опрос каждые 2 секунды  
    setInterval(fetchEquipmentStatus, 2000);
    fetchEquipmentStatus();
})();