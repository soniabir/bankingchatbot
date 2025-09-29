import os
import httpx
import streamlit as st

# ----------------------------
# Config
# ----------------------------
API_KEY = os.getenv("OPENAI_API_KEY", "KEY")
API_URL = "URL"
MODEL = "https://chat.deepseek.com/"


# ----------------------------
# Banking Chatbot Class
# ----------------------------
class BankingChatBot:
    def __init__(self, api_key: str = API_KEY, model: str = MODEL):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.context = [
            {"role": "system", "content": (
                "You are a helpful banking assistant. "
                "Answer user queries about account balance, transactions, loans, "
                "credit cards, and general banking services. "
                "If the query is outside banking, politely say you can only help with banking topics."
            )}
        ]

    def ask(self, user_input: str) -> str:
        """Send user query to the LLM and return the response."""
        self.context.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": self.context,
            "temperature": 0.5
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(API_URL, headers=self.headers, json=payload)
                resp.raise_for_status()
                reply = resp.json()["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as e:
            reply = f"Sorry, I encountered an API error: {e.response.status_code}. Please check your configuration."
        except Exception as e:
            reply = f"An unexpected error occurred: {e}"


        # Save conversation context
        self.context.append({"role": "assistant", "content": reply})
        return reply


# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Banking ChatBot", page_icon="🏦", layout="centered")
st.title("🏦 Banking ChatBot")
st.markdown("Ask me about your banking queries (loans, credit cards, balance, etc.)")

# --- Hardcoded Replies for the first 4 interactions ---
HARDCODED_REPLIES = [
    "Hello! Welcome to our bank's virtual assistant. I'm here to help you with your banking needs. How can I assist you today?",
    "Please Enter your Account number",
    "Please Enter OTP sent your Register Mobile number",
    "Your account balance is 1500000 "
]

# --- Session State Initialization ---
# Maintain chatbot instance in session state
if "bot" not in st.session_state:
    st.session_state.bot = BankingChatBot()

# Maintain message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# ADDED: Maintain a message counter
if "message_count" not in st.session_state:
    st.session_state.message_count = 0

# --- Chat History Display ---
# Display chat history from the session state
for msg in st.session_state.messages:
    role, text = msg
    with st.chat_message(role):
        st.markdown(text)

# --- Chat Input and Response Logic ---
# Handle user input
if user_input := st.chat_input("Type your message..."):
    # Display the user's message
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # MODIFIED: Determine the bot's reply
    # Use hardcoded replies for the first 4 messages
    if st.session_state.message_count < len(HARDCODED_REPLIES):
        bot_reply = HARDCODED_REPLIES[st.session_state.message_count]
    else:
        # After the first 4 messages, use the AI
        bot_reply = st.session_state.bot.ask(user_input)

    # ADDED: Increment the message counter after getting a reply
    st.session_state.message_count += 1
    
    # Display the bot's response
    st.session_state.messages.append(("assistant", bot_reply))
    with st.chat_message("assistant"):
        st.markdown(bot_reply)