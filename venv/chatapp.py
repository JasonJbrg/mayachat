import openai
import streamlit as st
import os
import googletrans
from streamlit_chat import message as msg
from translate import Translator
from pydub import AudioSegment
from pydub.playback import play
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("JBRG_OPEN_AI")

# Set page configuration
st.set_page_config(
    page_title="Maya Lingo",
    page_icon="/Users/jasons/PycharmProjects/pythonProject/venv/static/jedburghlogo_webicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Apply styles
streamlit_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Mono', monospace;
        background: #4F5223;
    }

    .custom-title {
        overflow: hidden;
        color: white;
        font-size: 1.3em;
        animation: typewriter 4s steps(50) 1s both;
        white-space: nowrap;
        padding-bottom: 50px;
    }
    @keyframes typewriter {
        0% {
            width: 0;
        }
        100% {
            width: 100%;
        }
    }
    </style>
"""





st.markdown(streamlit_style, unsafe_allow_html=True)
st.markdown('<h1 class="custom-title">WELCOME, AIRMAN ALLIE</h1>', unsafe_allow_html=True)




# Define the initial context for role-playing


st.subheader("ChatGPT عربي")
task_selection = st.selectbox("CHOOSE AN AI:",
                              ["Speaking with: Hamza, Cafe Owner", "Speaking with: Lael, Airline Ticket Official"])
st.write("***")

initial_context = {
    "Speaking with: Hamza, Cafe Owner": "You are the owner of a popular Cafe in Baghdad, Iraq. You have been running the cafe for several years and have built a strong network of customers and contacts. You are known for your keen observation skills and often hear about suspicious activities happening in the neighborhood, including potential terrorist activities. Recently, you witnessed a meeting between a group of individuals who raised your suspicions and you believe they might be involved in terrorist activities.",
    "Speaking with: Lael, Airline Ticket Official": "You are a customer service representative at an airline ticket office. You assist customers with their flight bookings, ticket changes, and travel inquiries. Your goal is to provide excellent service and ensure a smooth travel experience for passengers. Please provide the necessary details and information to assist the customers effectively."
}

translator = Translator(to_lang="en", from_lang="ar")

if 'hst_chat' not in st.session_state:
    st.session_state.hst_chat = []

user_prompt = st.text_input("Start your chat (in Arabic):")
btn_enter = st.button("Enter")
if btn_enter:
    st.session_state.hst_chat.append({"role": "user", "content": user_prompt})

    # Check if any word from the tcv.txt file is present in the user input
    tcv_file_path = "/Users/jasons/PycharmProjects/pythonProject/venv/tcv.txt"
    with open(tcv_file_path, "r", encoding="utf-8") as file:
        specific_words = [word.strip() for word in file.readlines()]

    user_input_words = user_prompt.split()  # Split the user input into individual words

    # Check if any word from the tcv.txt file is present in the user input
    matching_words = set(specific_words).intersection(user_input_words)

    if matching_words:
        # Play the ding sound
        ding_sound_path = "/Users/jasons/PycharmProjects/pythonProject/venv/audio/tcv_match.mp3"
        ding_sound = AudioSegment.from_file(ding_sound_path)
        play(ding_sound)

    conversation = [{"role": "assistant", "content": initial_context[task_selection]}] + st.session_state.hst_chat
    return_openai = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=500,
        n=1
    )
    assistant_response = return_openai['choices'][0]['message']['content']
    st.session_state.hst_chat.append({"role": "assistant", "content": assistant_response})

if len(st.session_state.get('hst_chat', [])) > 0:
    for i in range(len(st.session_state.hst_chat)):
        if i % 2 == 0:
            msg("You: " + st.session_state.hst_chat[i]['content'], is_user=True)
        else:
            msg("AI Arabic: " + st.session_state.hst_chat[i]['content'])

            # Add Translation button for AI responses
            translation_expander = st.expander("Show Translation")
            with translation_expander:
                translation_result = translator.translate(st.session_state.hst_chat[i]['content'])
                if isinstance(translation_result, str):
                    translation = translation_result
                else:
                    translation = translation_result.text
                st.write(translation)