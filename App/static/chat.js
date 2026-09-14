(function () {
    'use strict';

    var STATUS_URL = '/chat/status';
    var SEND_URL = '/chat';
    var HISTORY_LIMIT = 6;

    var launcher = document.getElementById('chat-launcher');
    var panel = document.getElementById('chat-panel');
    var closeBtn = document.getElementById('chat-close');
    var refreshBtn = document.getElementById('chat-refresh');
    var unavailableView = document.getElementById('chat-unavailable');
    var chattingView = document.getElementById('chat-chatting');
    var form = document.getElementById('chat-form');
    var input = document.getElementById('chat-input');
    var messages = document.getElementById('chat-messages');

    if (!launcher || !panel) {
        return;
    }

    var history = [];

    function showUnavailable() {
        unavailableView.hidden = false;
        chattingView.hidden = true;
    }

    function showChatting() {
        unavailableView.hidden = true;
        chattingView.hidden = false;
    }

    function checkStatus() {
        return fetch(STATUS_URL)
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data && data.available) {
                    showChatting();
                } else {
                    showUnavailable();
                }
            })
            .catch(function () {
                showUnavailable();
            });
    }

    function appendMessage(role, text) {
        var row = document.createElement('div');
        row.className = 'chat-message chat-message-' + role;
        row.textContent = text;
        messages.appendChild(row);
        messages.scrollTop = messages.scrollHeight;
    }

    function openPanel() {
        panel.hidden = false;
        launcher.setAttribute('aria-expanded', 'true');
        checkStatus();
    }

    function closePanel() {
        panel.hidden = true;
        launcher.setAttribute('aria-expanded', 'false');
    }

    launcher.addEventListener('click', function () {
        if (panel.hidden) {
            openPanel();
        } else {
            closePanel();
        }
    });

    closeBtn.addEventListener('click', closePanel);
    refreshBtn.addEventListener('click', checkStatus);

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        var text = input.value.trim();
        if (!text) {
            return;
        }

        appendMessage('user', text);
        var priorHistory = history.slice();
        history.push({ role: 'user', text: text });
        history = history.slice(-HISTORY_LIMIT);

        input.value = '';
        input.disabled = true;

        fetch(SEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history: priorHistory })
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('unavailable');
                }
                return response.json();
            })
            .then(function (data) {
                appendMessage('assistant', data.reply);
                history.push({ role: 'assistant', text: data.reply });
                history = history.slice(-HISTORY_LIMIT);
                input.disabled = false;
                input.focus();
            })
            .catch(function () {
                input.disabled = false;
                showUnavailable();
            });
    });
})();
