// Global Conversation History State
let conversationHistory = [];

// DOM Elements
const htmlElement = document.documentElement;
const themeToggleBtn = document.getElementById('theme-toggle');
const welcomeContainer = document.getElementById('welcome-container');
const chatMessagesContainer = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInputField = document.getElementById('user-input');

// 1. Theme Toggle Management
const savedTheme = localStorage.getItem('theme') || 'dark';
htmlElement.setAttribute('data-theme', savedTheme);

themeToggleBtn.addEventListener('click', () => {
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// 2. Select Suggestion handler
function selectSuggestion(queryText) {
    userInputField.value = queryText;
    userInputField.focus();
    // Automatically submit suggestion
    handleSubmit();
}

// 3. Append Message to Window
function appendMessage(role, content, extra = {}) {
    // Hide welcome view on first message
    if (!welcomeContainer.classList.contains('hidden')) {
        welcomeContainer.classList.add('hidden');
        chatMessagesContainer.classList.remove('hidden');
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    const textNode = document.createElement('p');
    
    // Check if it is a refusal or success status to color code warning
    if (extra.status === 'refused_advisory' || extra.status === 'refused_scope') {
        messageDiv.style.borderLeft = '4px solid #ef4444';
    }

    // Clean inline redundant footers if present (handled by formatting already)
    let cleanedContent = content;
    const sourceSplitIdx = cleanedContent.indexOf('\n\nSource:');
    if (sourceSplitIdx !== -1) {
        cleanedContent = cleanedContent.substring(0, sourceSplitIdx).trim();
    }
    
    textNode.textContent = cleanedContent;
    messageDiv.appendChild(textNode);

    // Append Citation Link if Bot success / refusal
    if (role === 'bot') {
        const citationDiv = document.createElement('div');
        citationDiv.className = 'citation-footer';
        
        let urlText = extra.source_url || 'https://groww.in';
        let dateText = extra.last_updated || new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-');
        
        const linkElem = document.createElement('a');
        linkElem.href = urlText;
        linkElem.target = '_blank';
        linkElem.className = 'citation-link';
        linkElem.textContent = `🔗 Source Page: ${urlText}`;
        
        const dateElem = document.createElement('span');
        dateElem.textContent = `📅 Last updated from sources: ${dateText}`;
        
        citationDiv.appendChild(linkElem);
        citationDiv.appendChild(dateElem);
        messageDiv.appendChild(citationDiv);
    }

    chatMessagesContainer.appendChild(messageDiv);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

// 4. Typing Indicator
let typingIndicatorElem = null;

function showTypingIndicator() {
    typingIndicatorElem = document.createElement('div');
    typingIndicatorElem.className = 'chat-message bot';
    typingIndicatorElem.id = 'typing-indicator';
    
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        indicatorDiv.appendChild(dot);
    }
    
    typingIndicatorElem.appendChild(indicatorDiv);
    chatMessagesContainer.appendChild(typingIndicatorElem);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

function removeTypingIndicator() {
    if (typingIndicatorElem) {
        typingIndicatorElem.remove();
        typingIndicatorElem = null;
    }
}

// 5. API Submission
async function handleSubmit(event) {
    if (event) event.preventDefault();
    
    const query = userInputField.value.trim();
    if (!query) return;
    
    // Append user query bubble
    appendMessage('user', query);
    addQueryToHistorySidebar(query);
    userInputField.value = '';
    
    // Show typing bubble
    showTypingIndicator();
    
    // Call FastAPI backend /api/chat
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                history: conversationHistory
            })
        });
        
        removeTypingIndicator();
        
        if (response.ok) {
            const data = await response.json();
            
            // Append assistant response bubble
            appendMessage('bot', data.answer, {
                source_url: data.source_url,
                last_updated: data.last_updated,
                status: data.status
            });
            
            // Update conversation history
            conversationHistory.push({ role: 'user', content: query });
            conversationHistory.push({ role: 'assistant', content: data.answer });
            
        } else {
            const errData = await response.text();
            appendMessage('bot', `Error: Failed to process request (HTTP ${response.status}). ${errData}`);
        }
        
    } catch (err) {
        removeTypingIndicator();
        appendMessage('bot', `Network error: Could not reach the server. Make sure the FastAPI backend is running.`);
        console.error(err);
    }
}

chatForm.addEventListener('submit', handleSubmit);

// 6. Left History Sidebar Helpers
function addQueryToHistorySidebar(query) {
    const queriesList = document.getElementById('history-queries-list');
    if (!queriesList) return;
    
    const placeholder = queriesList.querySelector('.no-history-placeholder');
    if (placeholder) {
        queriesList.innerHTML = '';
    }
    
    // Prevent duplicate entries in sidebar
    const existingItems = Array.from(queriesList.querySelectorAll('.history-query-item span'));
    const isDuplicate = existingItems.some(span => span.textContent === query);
    if (isDuplicate) return;
    
    const item = document.createElement('div');
    item.className = 'history-query-item';
    
    // Create query text block
    const textBlock = document.createElement('div');
    textBlock.className = 'history-query-text';
    textBlock.innerHTML = `💬 <span>${escapeHtml(query)}</span>`;
    textBlock.onclick = () => selectSuggestion(query);
    
    // Create individual delete button (reveals on hover via CSS)
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'item-delete-btn';
    deleteBtn.innerHTML = '×';
    deleteBtn.title = 'Remove query from history';
    deleteBtn.onclick = (e) => {
        e.stopPropagation(); // Prevent query re-trigger
        item.remove();
        if (queriesList.children.length === 0) {
            queriesList.innerHTML = '<div class="no-history-placeholder">No queries sent yet</div>';
        }
    };
    
    item.appendChild(textBlock);
    item.appendChild(deleteBtn);
    queriesList.appendChild(item);
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function clearChatHistory() {
    conversationHistory = [];
    
    // Clear message bubbles
    chatMessagesContainer.innerHTML = '';
    
    // Restore welcome greetings dashboard placeholder
    welcomeContainer.classList.remove('hidden');
    chatMessagesContainer.appendChild(welcomeContainer);
    
    // Reset left sidebar list
    const queriesList = document.getElementById('history-queries-list');
    if (queriesList) {
        queriesList.innerHTML = '<div class="no-history-placeholder">No queries sent yet</div>';
    }
}
