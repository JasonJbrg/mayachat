import openai
import streamlit as st
import os
from streamlit_chat import message as msg

openai.api_key = os.getenv("JBRG_OPEN_AI")
openai.api_key = "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"

st.title("ChatGPT Arabic")
task_selection = st.selectbox("Select Task-Based AI", ["Speaking with: Hamza, Cafe Owner", "Speaking with: Lael, Airline Ticket Official"])
st.write("***")

# Apply custom CSS styles inline
st.markdown(
    """
    <style>
    body {
        font-family: "IBM Plex Mono", monospace;
        background-color: #4F5223;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define the initial context for role-playing
initial_context = {
    "Speaking with: Hamza, Cafe Owner": "You are the owner of a popular Cafe in Baghdad, Iraq. You have been running the cafe for several years and have built a strong network of customers and contacts. You are known for your keen observation skills and often hear about suspicious activities happening in the neighborhood, including potential terrorist activities. Recently, you witnessed a meeting between a group of individuals who raised your suspicions and you believe they might be involved in terrorist activities.",
    "Speaking with: Lael, Airline Ticket Official": "You are a customer service representative at an airline ticket office. You assist customers with their flight bookings, ticket changes, and travel inquiries. Your goal is to provide excellent service and ensure a smooth travel experience for passengers. Please provide the necessary details and information to assist the customers effectively."
}

if 'hst_chat' not in st.session_state:
    st.session_state.hst_chat = []

user_prompt = st.text_input("Start your chat (in Arabic):")
btn_enter = st.button("Enter")
if btn_enter:
    st.session_state.hst_chat.append({"role": "user", "content": user_prompt})
    conversation = [{"role": "assistant", "content": initial_context[task_selection]}] + st.session_state.hst_chat
    return_openai = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=500,
        n=1
    )
    st.session_state.hst_chat.append(
        {"role": "assistant",
         "content": return_openai['choices'][0]['message']['content']})
    if len(st.session_state.hst_chat) > 0:
        for i in range(len(st.session_state.hst_chat)):
            if i % 2 == 0:
                msg("You: " + st.session_state.hst_chat[i]['content'], is_user=True)
            else:
                msg("AI Arabic: " + st.session_state.hst_chat[i]['content'])
