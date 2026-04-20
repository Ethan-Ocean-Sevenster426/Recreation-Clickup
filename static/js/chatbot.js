// Enhanced Chatbot JavaScript with Feedback and Satisfaction Tracking

document.addEventListener('DOMContentLoaded', function() {
    initChatbot();
});

function initChatbot() {
    console.log('Initializing enhanced chatbot with feedback system...');
    const chatbotButton = document.getElementById('chatbot-button');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const initialTimestamp = document.getElementById('initial-timestamp');

    if (!chatbotButton || !chatbotWindow) {
        console.error('Required chatbot elements not found');
        return;
    }

    let isOpen = false;
    let messages = [];
    let sessionId = generateSessionId();
    let conversationCount = 0;
    let hasShownWelcome = false;

    // Generate unique session ID
    function generateSessionId() {
        return 'session-' + Date.now() + '-' + Math.random().toString(36).substring(2, 11);
    }

    // Initialize timestamp
    if (initialTimestamp) {
        initialTimestamp.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    // Toggle chatbot
    function toggleChatbot() {
        isOpen = !isOpen;

        if (isOpen) {
            chatbotWindow.classList.add('chatbot-open');
            chatbotWindow.style.opacity = '1';
            chatbotWindow.style.visibility = 'visible';
            chatbotWindow.style.transform = 'scale(1) translateY(0)';
            chatbotWindow.style.pointerEvents = 'auto';
            chatbotButton.style.transform = 'scale(0)';
            chatbotButton.style.opacity = '0';

            setTimeout(() => {
                if (chatbotInput) chatbotInput.focus();
            }, 300);
        } else {
            chatbotWindow.classList.remove('chatbot-open');
            chatbotWindow.style.opacity = '0';
            chatbotWindow.style.visibility = 'hidden';
            chatbotWindow.style.transform = 'scale(0.8) translateY(20px)';
            chatbotWindow.style.pointerEvents = 'none';
            chatbotButton.style.transform = 'scale(1)';
            chatbotButton.style.opacity = '1';
        }
    }

    // Add message to chat
    function addMessage(text, isBot = false, isSpecial = false) {
        const message = {
            text: text,
            isBot: isBot,
            isSpecial: isSpecial,
            timestamp: new Date()
        };

        messages.push(message);
        renderMessage(message);
        scrollToBottom();

        if (!isBot) {
            conversationCount++;
        }
    }

    // Render a single message
    function renderMessage(message) {
        if (!chatbotMessages) return;

        const isDark = document.documentElement.classList.contains('dark');
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-2 flex ${message.isBot ? 'justify-start' : 'justify-end'}`;

        const bubbleClass = message.isBot
            ? (isDark ? 'bg-gray-700 border border-gray-600 text-gray-100' : 'bg-white border border-gray-200 text-gray-800')
            : (isDark ? 'bg-accent text-white' : 'bg-red-600 text-white');

        messageDiv.innerHTML = `
            <div class="max-w-[80%] rounded-lg p-2.5 ${bubbleClass}">
                <p class="text-sm leading-snug">${message.text}</p>
                <p class="text-xs mt-0.5 ${isDark ? 'opacity-50' : 'opacity-70'}">
                    ${message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </p>
            </div>
        `;

        chatbotMessages.appendChild(messageDiv);
    }

    // Ask for satisfaction rating
    function askForSatisfaction() {
        // Don't show if one is already visible
        if (document.getElementById('satisfaction-prompt')) return;

        const isDark = document.documentElement.classList.contains('dark');
        const satisfactionDiv = document.createElement('div');
        satisfactionDiv.className = 'mb-4 flex justify-start';
        satisfactionDiv.id = 'satisfaction-prompt';

        const textClass = isDark ? 'text-gray-100' : 'text-gray-800';

        const emojiOptions = [
            { rating: 1, emoji: '😞', label: 'Very Unsatisfied' },
            { rating: 2, emoji: '😐', label: 'Unsatisfied' },
            { rating: 3, emoji: '😊', label: 'Satisfied' },
            { rating: 4, emoji: '😄', label: 'Very Satisfied' }
        ];

        satisfactionDiv.innerHTML = `
            <div class="p-3 max-w-[90%]">
                <p class="text-sm ${textClass} mb-3 font-semibold">Before we start, how would you rate our website so far?</p>
                <div class="flex gap-2 mb-2 justify-center" style="user-select: none;">
                    ${emojiOptions.map(option => `
                        <div onclick="window.submitSatisfaction(${option.rating})"
                             class="satisfaction-option"
                             style="display: flex; flex-direction: column; align-items: center; padding: 0.375rem 0.5rem; cursor: pointer; ${isDark ? 'color: white;' : ''}"
                             title="${option.label}">
                            <span style="font-size: 1.5rem; line-height: 1; pointer-events: none;">${option.emoji}</span>
                            <span style="font-size: 0.625rem; margin-top: 0.25rem; pointer-events: none;">${option.rating}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        chatbotMessages.appendChild(satisfactionDiv);
        scrollToBottom();
    }

    // Submit satisfaction rating
    window.submitSatisfaction = async function(rating) {
        const satisfactionPrompt = document.getElementById('satisfaction-prompt');
        if (satisfactionPrompt) satisfactionPrompt.remove();

        try {
            const response = await fetch('/chatbot/satisfaction/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rating: rating,
                    session_id: sessionId,
                    conversation_context: getConversationContext()
                })
            });

            const data = await response.json();

            if (data.success) {
                const emojiMap = { 1: '😞', 2: '😐', 3: '😊', 4: '😄' };
                addMessage(`Thank you for your feedback ${emojiMap[rating]}! This helps us improve our service. 🙏`, true);

                // Ask for additional feedback
                setTimeout(() => {
                    askForTextFeedback();
                }, 1500);
            }
        } catch (error) {
            console.error('Error submitting satisfaction:', error);
        }
    };


    // Ask for text feedback
    function askForTextFeedback() {
        const isDark = document.documentElement.classList.contains('dark');
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'mb-4 flex justify-start';
        feedbackDiv.id = 'feedback-prompt';

        const bgClass = isDark ? 'bg-gray-700 border border-gray-600' : 'bg-white border border-gray-200';
        const textClass = isDark ? 'text-gray-100' : 'text-gray-800';
        const inputBgClass = isDark ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';

        feedbackDiv.innerHTML = `
            <div class="${bgClass} rounded-lg p-3 max-w-[85%]">
                <p class="text-sm ${textClass} mb-2">Would you like to share any additional feedback? 💭</p>
                <textarea id="feedback-text"
                          class="w-full p-2 rounded-lg border ${inputBgClass} text-sm resize-none"
                          rows="3"
                          placeholder="Your feedback helps us improve..."></textarea>
                <div class="flex gap-2 mt-2">
                    <button onclick="window.submitTextFeedback()"
                            class="px-3 py-1 rounded-lg text-sm font-semibold transition-all ${
                                isDark ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-red-600 hover:bg-red-700 text-white'
                            }">
                        Submit
                    </button>
                    <button onclick="window.skipTextFeedback()"
                            class="px-3 py-1 rounded-lg text-sm font-semibold transition-all ${
                                isDark ? 'bg-gray-600 hover:bg-gray-700 text-white' : 'bg-gray-300 hover:bg-gray-400 text-gray-800'
                            }">
                        Skip
                    </button>
                </div>
            </div>
        `;

        chatbotMessages.appendChild(feedbackDiv);
        scrollToBottom();
    }

    // Submit text feedback
    window.submitTextFeedback = async function() {
        const feedbackText = document.getElementById('feedback-text')?.value || '';
        const feedbackPrompt = document.getElementById('feedback-prompt');
        if (feedbackPrompt) feedbackPrompt.remove();

        if (!feedbackText.trim()) {
            addMessage("Thank you anyway! Feel free to chat anytime. 😊", true);
            return;
        }

        try {
            const response = await fetch('/chatbot/feedback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feedback_type: 'general',
                    feedback_text: feedbackText,
                    session_id: sessionId,
                    conversation_context: getConversationContext()
                })
            });

            const data = await response.json();

            if (data.success) {
                addMessage("Thank you for your valuable feedback! We'll use it to improve our service. 🙏", true);
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            addMessage("Thanks for your feedback! We appreciate your input. 😊", true);
        }
    };

    // Skip text feedback
    window.skipTextFeedback = function() {
        const feedbackPrompt = document.getElementById('feedback-prompt');
        if (feedbackPrompt) feedbackPrompt.remove();
        addMessage("No problem! Thanks for chatting with me! 😊", true);
    };

    // Get conversation context (last 5 messages)
    function getConversationContext() {
        return messages.slice(-5).map(m => ({
            text: m.text,
            isBot: m.isBot,
            timestamp: m.timestamp.toISOString()
        }));
    }

    // Handle theme switching
    function handleThemeInput(input) {
        const normalizedInput = input.toLowerCase().trim();

        if (normalizedInput.includes('dark') ||
            normalizedInput.includes('night') ||
            normalizedInput.includes('dark mode') ||
            normalizedInput.includes('i want dark') ||
            normalizedInput.includes('switch to dark') ||
            normalizedInput.includes('make it dark')) {

          localStorage.setItem('theme', 'dark');
          document.documentElement.classList.add('dark');
          return 'Switching to dark mode! 🌙 Enjoy the darker interface.';
        }

        if (normalizedInput.includes('light') ||
            normalizedInput.includes('day') ||
            normalizedInput.includes('light mode') ||
            normalizedInput.includes('i want light') ||
            normalizedInput.includes('switch to light') ||
            normalizedInput.includes('make it light')) {

          localStorage.setItem('theme', 'light');
          document.documentElement.classList.remove('dark');
          return 'Switching to light mode! ☀️ Enjoy the brighter interface.';
        }

        return null;
    }

    // Check if user wants to give feedback
    function checkFeedbackIntent(query) {
        const lowerQuery = query.toLowerCase();
        if (lowerQuery.includes('feedback') ||
            lowerQuery.includes('complain') ||
            lowerQuery.includes('suggest') ||
            lowerQuery.includes('improve')) {
            return true;
        }
        return false;
    }

    // Generate bot response using AI service
    async function generateBotResponse(query) {
        // First check if it's a theme request
        const themeResponse = handleThemeInput(query);
        if (themeResponse) {
            return themeResponse;
        }

        // Check if user wants to give feedback
        if (checkFeedbackIntent(query)) {
            setTimeout(() => {
                askForTextFeedback();
            }, 1000);
            return "I'd love to hear your feedback! Let me help you share that with our team.";
        }

        // Use AI service for intelligent responses
        try {
            const response = await fetch('/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: query,
                    user_id: '',
                    session_id: sessionId
                })
            });

            const data = await response.json();

            if (data.answer) {
                return data.answer;
            } else {
                // Fallback response if AI fails
                return "I'm here to help! Could you tell me more about what you're looking for?";
            }
        } catch (error) {
            console.error('AI service error:', error);
            // Fallback to basic response on error
            return "I'm having a bit of trouble right now, but I'm here to help! Please try again or visit our contact page.";
        }
    }

    // Scroll to bottom
    function scrollToBottom() {
        if (chatbotMessages) {
            setTimeout(() => {
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
            }, 100);
        }
    }

    // Show typing indicator
    function showTypingIndicator() {
        if (!chatbotMessages) return;

        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'flex justify-start mb-4';

        const isDark = document.documentElement.classList.contains('dark');
        const bgClass = isDark ? 'bg-gray-700 border border-gray-600' : 'bg-white border border-gray-200';
        const dotClass = isDark ? 'bg-gray-500' : 'bg-gray-300';

        typingDiv.innerHTML = `
            <div class="${bgClass} rounded-lg p-3">
                <div class="flex space-x-2">
                    <div class="w-2 h-2 rounded-full ${dotClass} animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 rounded-full ${dotClass} animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 rounded-full ${dotClass} animate-bounce" style="animation-delay: 300ms"></div>
                </div>
            </div>
        `;

        chatbotMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    // Hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Handle form submission
    async function handleSubmit(e) {
        e.preventDefault();

        const userInput = chatbotInput.value.trim();
        if (!userInput) return;

        // Add user message
        addMessage(userInput, false);
        chatbotInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        // Generate and show bot response using AI service
        try {
            const botResponse = await generateBotResponse(userInput);
            hideTypingIndicator();
            addMessage(botResponse, true);

            // Show satisfaction prompt after first message and then every 6 messages (1, 7, 13, 19...)
            if ((conversationCount - 1) % 6 === 0 && conversationCount > 0) {
                setTimeout(() => {
                    askForSatisfaction();
                }, 1500);
            }
        } catch (error) {
            console.error('Error getting bot response:', error);
            hideTypingIndicator();
            addMessage("I apologize, but I'm having trouble responding right now. Please try again!", true);
        }
    }

    // Update input state
    function updateInputState() {
        const submitButton = chatbotForm?.querySelector('button[type="submit"]');
        if (submitButton && chatbotInput) {
            submitButton.disabled = !chatbotInput.value.trim();
        }
    }

    // Bind event listeners
    if (chatbotButton) {
        chatbotButton.addEventListener('click', toggleChatbot);
    }

    if (chatbotClose) {
        chatbotClose.addEventListener('click', toggleChatbot);
    }

    if (chatbotForm) {
        chatbotForm.addEventListener('submit', handleSubmit);
    }

    if (chatbotInput) {
        chatbotInput.addEventListener('input', updateInputState);
        chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
            }
        });
    }

    // Close chatbot when clicking outside
    document.addEventListener('click', (e) => {
        if (isOpen && !chatbotWindow.contains(e.target) && !chatbotButton.contains(e.target)) {
            toggleChatbot();
        }
    });

    // Initialize input state
    updateInputState();
}
