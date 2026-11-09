const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const convList = document.getElementById('conv-list');
const newConvBtn = document.getElementById('new-conv');

let currentSessionId = null;

// Theme management
const savedTheme = localStorage.getItem('akari-theme') || 'theme-kyoto';
body.className = savedTheme;

themeToggle.addEventListener('click', () => {
    const newTheme = body.classList.contains('theme-kyoto') ? 'theme-zen' : 'theme-kyoto';
    body.className = newTheme;
    localStorage.setItem('akari-theme', newTheme);
});

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    messageInput.value = '';

    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: currentSessionId,
                message: text,
                mode: 'default'
            })
        });
        const data = await resp.json();
        if (data.response) {
            appendMessage('assistant', data.response);
            currentSessionId = data.session_id;
            loadConversations();
        } else {
            appendMessage('assistant', 'ごめんなさい、エラーが発生しました。');
        }
    } catch (err) {
        console.error(err);
        appendMessage('assistant', 'サーバーに接続できません。');
    }
}

function appendMessage(role, text) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.textContent = text;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function loadConversations() {
    const resp = await fetch('/api/conversations');
    const data = await resp.json();
    convList.innerHTML = '';
    data.conversations.forEach(c => {
        const div = document.createElement('div');
        div.className = `conv-item ${c.session_id === currentSessionId ? 'active' : ''}`;
        div.textContent = `会話: ${c.session_id}`;
        div.onclick = () => loadSession(c.session_id);
        convList.appendChild(div);
    });
}

async function loadSession(sid) {
    currentSessionId = sid;
    messagesDiv.innerHTML = '';
    const resp = await fetch(`/api/conversations/${sid}`);
    const data = await resp.json();
    data.messages.forEach(m => appendMessage(m.role, m.content));
    loadConversations();
}

newConvBtn.onclick = () => {
    currentSessionId = null;
    messagesDiv.innerHTML = '';
    document.getElementById('conv-title').textContent = '新しい会話';
};

loadConversations();
