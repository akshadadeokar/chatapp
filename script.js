const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

const communityBox = document.getElementById("community-box");
const communityInput = document.getElementById("community-input");
const communitySend = document.getElementById("community-send");

const API_BASE_URL = "http://127.0.0.1:5000"; // Your Flask backend URL

function appendMessage(container, message, className) {
  const msgDiv = document.createElement("div");
  msgDiv.className = className;
  msgDiv.textContent = message;
  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

// Function to append community messages (with timestamp if available)
function appendCommunityMessage(message, timestamp = null) {
  const msgDiv = document.createElement("div");
  msgDiv.className = "community-message";
  let displayMessage = message;
  if (timestamp) {
    const date = new Date(timestamp);
    displayMessage = `${message} (${date.toLocaleString()})`;
  }
  msgDiv.textContent = displayMessage;
  communityBox.appendChild(msgDiv);
  communityBox.scrollTop = communityBox.scrollHeight;
}

// Handle chatbot messages
sendBtn.addEventListener("click", async () => {
  const message = userInput.value.trim();
  if (!message) return;
  appendMessage(chatBox, message, "message user-message");
  userInput.value = "";

  const loadingMsg = document.createElement("div");
  loadingMsg.className = "message bot-message";
  loadingMsg.textContent = "Thinking...";
  chatBox.appendChild(loadingMsg);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message })
    });

    const data = await response.json();
    loadingMsg.remove();
    appendMessage(chatBox, data.reply, "message bot-message");
  } catch (error) {
    console.error("Error communicating with chatbot API:", error);
    loadingMsg.remove();
    appendMessage(chatBox, "Error: Could not connect to the chatbot.", "message bot-message");
  }
});

// Handle community chat (now interacting with backend)
communitySend.addEventListener("click", async () => {
  const msg = communityInput.value.trim();
  if (!msg) return;

  try {
    const response = await fetch(`${API_BASE_URL}/community/post`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });

    const data = await response.json();
    if (data.status === "success") {
      // Re-fetch messages to get the latest, including the one just sent
      await fetchCommunityMessages();
      communityInput.value = "";
    } else {
      console.error("Error posting community message:", data.message);
      alert("Failed to send community message.");
    }
  } catch (error) {
    console.error("Network error posting community message:", error);
    alert("Could not connect to the community server.");
  }
});

// Function to fetch and display community messages
async function fetchCommunityMessages() {
  try {
    const response = await fetch(`${API_BASE_URL}/community/messages`);
    const messages = await response.json();
    communityBox.innerHTML = ""; // Clear existing messages
    messages.forEach(msg => {
      appendCommunityMessage(msg.message, msg.timestamp);
    });
  } catch (error) {
    console.error("Error fetching community messages:", error);
    // Optionally display an error in the community box
    appendCommunityMessage("Error loading community messages.", null);
  }
}

// Fetch community messages when the page loads
document.addEventListener("DOMContentLoaded", fetchCommunityMessages);