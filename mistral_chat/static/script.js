const chatWindow = document.getElementById("chatWindow");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const clearButton = document.getElementById("clearButton");
const formatSelect = document.getElementById("formatSelect");

let history = [];
let typingBubble = null;

function appendBubble(content, role) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role === "user" ? "user-message" : "ai-message"}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;

  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return wrapper;
}

function showTypingIndicator() {
  typingBubble = appendBubble("...", "assistant");
  typingBubble.classList.add("typing");
}

function hideTypingIndicator() {
  if (typingBubble) {
    typingBubble.remove();
    typingBubble = null;
  }
}

function setSending(isSending) {
  sendButton.disabled = isSending;
  messageInput.disabled = isSending;
}

async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  appendBubble(message, "user");
  messageInput.value = "";
  setSending(true);
  showTypingIndicator();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        history,
        format: formatSelect.value,
      }),
    });

    const data = await response.json();
    hideTypingIndicator();

    if (!response.ok) {
      appendBubble(data.error || "Something went wrong.", "assistant");
      return;
    }

    history = data.history || [];
    appendBubble(data.reply, "assistant");
  } catch (error) {
    hideTypingIndicator();
    appendBubble("Network error. Please try again.", "assistant");
  } finally {
    setSending(false);
    messageInput.focus();
  }
}

async function clearChat() {
  try {
    const response = await fetch("/clear", { method: "POST" });
    const data = await response.json();
    history = data.history || [];
    chatWindow.innerHTML = "";
    appendBubble("Chat cleared. What should we talk about next?", "assistant");
  } catch (error) {
    appendBubble("Could not clear the chat right now.", "assistant");
  }
}

sendButton.addEventListener("click", sendMessage);
clearButton.addEventListener("click", clearChat);
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});
