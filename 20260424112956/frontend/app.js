/**
 * 智能运维助手 - 前端应用
 */

const API_BASE = '/api';

class ChatApp {
    constructor() {
        this.sessionId = 'default';
        this.isLoading = false;
        this.skills = [];

        this.initElements();
        this.bindEvents();
        this.loadSessions();
        this.loadSkills();
    }

    initElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.sessionList = document.getElementById('sessionList');
        this.skillList = document.getElementById('skillList');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.intentBadge = document.getElementById('intentBadge');
        this.currentSessionTitle = document.getElementById('currentSessionTitle');
    }

    bindEvents() {
        // 发送消息
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 输入框自动调整高度
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
            this.sendBtn.disabled = !this.messageInput.value.trim();
        });

        // 新建对话
        document.getElementById('newChatBtn').addEventListener('click', () => this.createNewSession());

        // 清除历史
        document.getElementById('clearHistory').addEventListener('click', () => this.clearHistory());

        // 侧边栏切换
        document.getElementById('toggleSidebar').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });

        document.getElementById('openSidebar')?.addEventListener('click', () => {
            document.getElementById('sidebar').classList.add('open');
        });

        // 快捷操作
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                this.messageInput.value = message;
                this.sendMessage();
            });
        });
    }

    async loadSessions() {
        try {
            const res = await fetch(`${API_BASE}/sessions`);
            const sessions = await res.json();

            this.sessionList.innerHTML = '';
            sessions.forEach(sid => {
                const item = document.createElement('button');
                item.className = `session-item ${sid === this.sessionId ? 'active' : ''}`;
                item.innerHTML = `<i class="fas fa-comment"></i> ${sid}`;
                item.addEventListener('click', () => this.switchSession(sid));
                this.sessionList.appendChild(item);
            });
        } catch (e) {
            console.error('加载会话列表失败:', e);
        }
    }

    async loadSkills() {
        try {
            const res = await fetch(`${API_BASE}/skills`);
            this.skills = await res.json();

            this.skillList.innerHTML = '';
            const icons = {
                'add_user': 'fa-user-plus',
                'delete_user': 'fa-user-minus',
                'add_resource': 'fa-server',
                'delete_resource': 'fa-trash',
                'sso': 'fa-key',
            };

            this.skills.forEach(skill => {
                const item = document.createElement('div');
                item.className = 'skill-item';
                item.innerHTML = `
                    <i class="fas ${icons[skill.intent] || 'fa-cog'}"></i>
                    <span>${skill.name}</span>
                    <span class="skill-desc">${skill.description}</span>
                `;
                this.skillList.appendChild(item);
            });
        } catch (e) {
            console.error('加载 Skills 失败:', e);
        }
    }

    async createNewSession() {
        try {
            const res = await fetch(`${API_BASE}/sessions/new`, { method: 'POST' });
            const data = await res.json();
            this.sessionId = data.session_id;
            this.chatMessages.innerHTML = '';
            this.welcomeScreen.style.display = 'flex';
            this.chatMessages.appendChild(this.welcomeScreen);
            this.currentSessionTitle.textContent = `会话 ${this.sessionId}`;
            this.intentBadge.style.display = 'none';
            await this.loadSessions();
        } catch (e) {
            console.error('创建会话失败:', e);
        }
    }

    async switchSession(sessionId) {
        this.sessionId = sessionId;
        this.currentSessionTitle.textContent = `会话 ${sessionId}`;

        // 加载历史消息
        try {
            const res = await fetch(`${API_BASE}/history/${sessionId}`);
            const data = await res.json();
            this.renderHistory(data.messages);
        } catch (e) {
            console.error('加载历史失败:', e);
        }

        await this.loadSessions();
    }

    renderHistory(messages) {
        this.chatMessages.innerHTML = '';

        if (messages.length === 0) {
            this.chatMessages.appendChild(this.welcomeScreen);
            this.welcomeScreen.style.display = 'flex';
            return;
        }

        this.welcomeScreen.style.display = 'none';
        messages.forEach(msg => {
            if (msg.role === 'human') {
                this.appendMessage('user', msg.content);
            } else if (msg.role === 'ai') {
                const meta = msg.intent ? [{ type: 'intent', text: msg.intent }] : [];
                this.appendMessage('ai', msg.content, meta);
            }
        });

        this.scrollToBottom();
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;

        // 隐藏欢迎屏
        this.welcomeScreen.style.display = 'none';

        // 添加用户消息
        this.appendMessage('user', message);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.sendBtn.disabled = true;

        // 显示加载状态
        this.isLoading = true;
        const typingEl = this.appendTypingIndicator();

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                }),
            });

            const data = await res.json();

            // 移除加载状态
            typingEl.remove();

            // 添加 AI 回复
            const meta = [];
            if (data.intent) {
                meta.push({ type: 'intent', text: data.intent });
            }
            if (data.skill_executed) {
                meta.push({ type: 'skill', text: 'Skill 已执行' });
            }

            this.appendMessage('ai', data.reply, meta);

            // 更新意图标签
            if (data.intent) {
                this.intentBadge.textContent = data.intent;
                this.intentBadge.className = 'intent-badge';
                if (['add_user', 'delete_user', 'add_resource', 'delete_resource', 'sso'].includes(data.intent)) {
                    this.intentBadge.classList.add('skill');
                } else if (data.intent === 'faq') {
                    this.intentBadge.classList.add('faq');
                }
                this.intentBadge.style.display = 'inline-block';
            }

            // 刷新会话列表
            await this.loadSessions();

        } catch (e) {
            typingEl.remove();
            this.appendMessage('ai', '抱歉，发生了错误，请稍后重试。');
            console.error('发送消息失败:', e);
        } finally {
            this.isLoading = false;
        }
    }

    appendMessage(role, content, meta = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;

        const avatarIcon = role === 'user' ? 'fa-user' : 'fa-robot';
        const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

        let metaHtml = '';
        if (meta.length > 0) {
            metaHtml = `<div class="message-meta">
                ${meta.map(m => `<span class="meta-tag ${m.type}">${m.text}</span>`).join('')}
                <span class="meta-tag time">${time}</span>
            </div>`;
        } else {
            metaHtml = `<div class="message-meta"><span class="meta-tag time">${time}</span></div>`;
        }

        // 简单的文本格式化
        const formattedContent = content
            .replace(/\n/g, '<br>')
            .replace(/• /g, '&bull; ');

        msgDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${avatarIcon}"></i>
            </div>
            <div>
                <div class="message-content">${formattedContent}</div>
                ${metaHtml}
            </div>
        `;

        this.chatMessages.appendChild(msgDiv);
        this.scrollToBottom();
        return msgDiv;
    }

    appendTypingIndicator() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message ai';
        msgDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(msgDiv);
        this.scrollToBottom();
        return msgDiv;
    }

    async clearHistory() {
        if (!confirm('确认清除当前会话的历史记录？')) return;

        try {
            await fetch(`${API_BASE}/history/${this.sessionId}`, { method: 'DELETE' });
            this.chatMessages.innerHTML = '';
            this.chatMessages.appendChild(this.welcomeScreen);
            this.welcomeScreen.style.display = 'flex';
            this.intentBadge.style.display = 'none';
        } catch (e) {
            console.error('清除历史失败:', e);
        }
    }

    scrollToBottom() {
        requestAnimationFrame(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        });
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});
