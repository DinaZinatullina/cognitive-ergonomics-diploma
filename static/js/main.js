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

})();