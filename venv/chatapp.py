import openai
import streamlit as st
from streamlit_chat import message as msg
from translate import Translator
from pydub import AudioSegment
from pydub.playback import play
import os
from dotenv import load_dotenv
import json
import docx
import io
from docx import Document
from datetime import datetime
import random

# Load environment variables from .env file
dotenv_path = "PycharmProjects/.env"
load_dotenv(dotenv_path)

# Read the config.json file
with open("venv/config.json") as file:
    config = json.load(file)

# Extract the values from the config dictionary
task_selection = config["task_selection"]
initial_context = {
    task: f"{config['initial_context'][task]} Please provide brief and concise responses."
    for task in task_selection
}
greetings = config["greetings"]

load_dotenv('/Users/jasons/PycharmProjects/pythonProject/PycharmProjects/.env')

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page configuration
st.set_page_config(
    page_title="Maya Lingo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define the CSS styles
streamlit_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&display=swap');

    #root {
        font-family: 'IBM Plex Mono', monospace !important;
        background-color: #4F5223 !important;
        color: white !important;
    }
    .custom-title {
        overflow: hidden;
        color: white;
        font-size: 1.3em;
        animation: typewriter 4s steps(50) 1s both;
        white-space: nowrap;
        padding-bottom: 50px;

    }
         /* Hide the Streamlit footer */
    .reportview-container .main footer {
        visibility: hidden;
    }

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
# Add a default option to the languages dictionary
languages = {'Select...': ''}

languages.update({
    'Chinese': 'zh',
    'Russian': 'ru',
    'Arabic': 'ar',
    'Japanese': 'ja',
    'Farsi': 'fa',
    'Spanish': 'es',
    'German': 'de',
    'Levantine Arabic': 'apc'  # ISO 639-3 code for Levantine Arabic
})

# Define default values for selected_language and selected_task
selected_language = 'Select...'
selected_task = 'Select...'

# Get user input for language selection
selected_language = st.selectbox("Select your language", list(languages.keys()), key='language_selection')

if selected_language != 'Select...':
    # Initialize the Translator with the selected language
    translator = Translator(to_lang="en", from_lang=languages[selected_language], provider="mymemory", secret_access_key="jason@jedburghco.com")

    # Add a default option to the task_selection list
    task_selection = ['Select...'] + task_selection

    # Get user input for task selection
    selected_task = st.selectbox("Select a task", task_selection, key='task_selection')

    # Only update the selected task in session state if a task is selected
    if selected_task != 'Select...':
        st.session_state.selected_task = selected_task
else:
    st.session_state.selected_task = None  # Set to None or some default value

# Initialize two Translator objects with appropriate language settings
translator_to_en = Translator(from_lang=languages[selected_language], to_lang="en", provider="mymemory", secret_access_key="jason@jedburghco.com")
translator_from_en = Translator(from_lang="en", to_lang=languages[selected_language], provider="mymemory", secret_access_key="jason@jedburghco.com")


# Apply styles
st.markdown(streamlit_style, unsafe_allow_html=True)

# Add a default option to the task_selection list
task_selection = ['Select...'] + task_selection

# Initialize chat history in session state if not already present
if 'hst_chat' not in st.session_state:
    st.session_state.hst_chat = []
if 'hst_chat_time' not in st.session_state:
    st.session_state.hst_chat_time = []

# Only proceed if a task is selected and the chat history is empty
if selected_task != 'Select...' and not st.session_state.hst_chat:
    # Update the selected task in session state
    st.session_state.selected_task = selected_task
    # Choose a random greeting for the selected task
    greeting = random.choice(greetings[selected_task])
    # Translate the greeting to the target language using translator_from_en
    greeting_translated = translator_from_en.translate(greeting)
    st.session_state.hst_chat.append({"role": "assistant", "content": greeting_translated})
    st.session_state.hst_chat_time.append(datetime.now())


# Update the selected task in session state
st.session_state.selected_task = selected_task



# Get user input
if selected_language != 'Select...':
    user_prompt = st.text_input(f"Start your chat (in {selected_language}):")
else:
    user_prompt = ''
btn_enter = st.button("Enter")

MAX_TOKENS = 500
MAX_TOKENS_PER_MESSAGE = 50

# Define a function to get the initial context
def get_initial_context(task):
    if task is not None and task in initial_context:
        return initial_context[task]
    else:
        return "Please select a task."
        
# Prepare the conversation for the chat model
conversation = [
    {"role": "assistant", "content": initial_context[st.session_state.selected_task]},
    {"role": "user", "content": user_prompt},  # use original prompt
] + st.session_state.hst_chat



# Only generate a response if the last message was from the user
if conversation[-1]["role"] == "user":
    # Use OpenAI API to get a response from the chat model
    return_openai = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=MAX_TOKENS,
        n=1
    )



# When 'Enter' button is clicked
if btn_enter and user_prompt:
    # Translate user's input to English
    user_prompt_translated = translator_to_en.translate(user_prompt)

    # Add user's translated response to the chat history
    st.session_state.hst_chat.append({"role": "user", "content": user_prompt})
    st.session_state.hst_chat_time.append(datetime.now())

    # Add user's translated response to the conversation
    conversation.append({"role": "user", "content": user_prompt_translated})

    # Only generate a response if the last message was from the user
    if st.session_state.hst_chat[-2]["role"] == "user":
        # Use OpenAI API to get a response from the chat model
        return_openai = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=MAX_TOKENS,
            n=1
        )

        # Add assistant's response to the chat history
        assistant_response = return_openai['choices'][0]['message']['content']
        st.session_state.hst_chat.append({"role": "assistant", "content": assistant_response})
        st.session_state.hst_chat_time.append(datetime.now())

    

    # Calculate the total number of tokens in the conversation
    total_tokens = sum(len(message['content'].split()) for message in conversation)

    # Check if the total tokens exceed the maximum allowed limit
    if total_tokens > MAX_TOKENS:
        # Remove messages until the total tokens is below the limit
        excess_tokens = total_tokens - MAX_TOKENS
        removed_tokens = 0
        removed_messages = 0

        # Iterate through the conversation messages from the beginning
        for i in range(len(conversation) - 1, -1, -1):
            message_tokens = len(conversation[i]['content'].split())
            if removed_tokens + message_tokens <= excess_tokens:
                # Remove the entire message
                removed_tokens += message_tokens
                removed_messages += 1
            else:
                # Remove a portion of the message
                tokens_to_remove = excess_tokens - removed_tokens
                conversation[i]['content'] = ' '.join(conversation[i]['content'].split()[:-tokens_to_remove])
                break

        # Remove the excess messages from the conversation
        conversation = conversation[:-removed_messages]

        # Split messages into multiple parts if they exceed the maximum tokens per message
        split_conversation = []
        current_message = {"role": conversation[0]["role"], "content": ""}
        for message in conversation[1:]:
            tokens_in_message = len(message["content"].split())
            if len(current_message["content"].split()) + tokens_in_message > MAX_TOKENS_PER_MESSAGE:
                split_conversation.append(current_message)
                current_message = {"role": message["role"], "content": message["content"]}
            else:
                current_message["content"] += " " + message["content"]

        if current_message["content"]:
            split_conversation.append(current_message)


        # Use OpenAI API to get a response from the chat model
        responses = []
        for split_message in split_conversation:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[split_message],
                max_tokens=MAX_TOKENS_PER_MESSAGE,
                n=1
            )
            responses.append(response['choices'][0]['message']['content'])

        # Add assistant's response to the chat history
        for response in responses:
            assistant_response = response
            st.session_state.hst_chat.append({"role": "assistant", "content": assistant_response})
            st.session_state.hst_chat_time.append(datetime.now())
    else:
        # Use OpenAI API to get a response from the chat model
        return_openai = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=MAX_TOKENS,
            n=1
        )

        # Add assistant's response to the chat history
        assistant_response = return_openai['choices'][0]['message']['content']
        st.session_state.hst_chat.append({"role": "assistant", "content": assistant_response})
        st.session_state.hst_chat_time.append(datetime.now())

    

# Display chat history
if st.session_state.hst_chat:
    for i in range(len(st.session_state.hst_chat)):
        if st.session_state.hst_chat[i]["role"] == "user":
            st.markdown(
                f"<div style='text-align: left; color: black; background-color: rgba(206, 187, 163, 0.5); '>You: {st.session_state.hst_chat[i]['content']}</div>",
                unsafe_allow_html=True)
        elif st.session_state.hst_chat[i]["role"] == "assistant":
            st.markdown(
                f"<div style='text-align: left; color: black; background-color: rgba(206, 187, 163, 1.0);'>{st.session_state.selected_task}: {st.session_state.hst_chat[i]['content']}</div>",
                unsafe_allow_html=True)

        # Translation expander for user input
        if i % 2 == 0:
            translation_expander = st.expander("Show User Translation", expanded=False)
            with translation_expander:
                # Use translator_to_en for user's messages
                translation_result = translator_to_en.translate(st.session_state.hst_chat[i]['content'])
                st.write(translation_result)

        # Translation expander for assistant responses
        else:
            translation_expander = st.expander("Show Assistant Translation")
            with translation_expander:
                # Use translator_from_en for assistant's responses
                translation_result = translator_from_en.translate(st.session_state.hst_chat[i]['content'])
                st.write(translation_result)

# If chat history exists, show the 'Save & Export' button
btn_save = st.button("Save & Export")
if btn_save:
    # Create a Word document with chat history
    doc = Document()

    # Add the current date and time to the document
    doc.add_paragraph(datetime.now().strftime('%m/%d/%Y %I:%M:%S %p'))

    # Calculate the total duration
    total_duration = st.session_state.hst_chat_time[-1] - st.session_state.hst_chat_time[0]

    # Add the total duration to the document
    doc.add_paragraph(f"Total Duration: {total_duration}")

    # Add the chat history to the document
    for message in st.session_state.hst_chat:
        doc.add_paragraph(f"{message['role']}: {message['content']}")

    # Save the Document into memory
    f = io.BytesIO()
    doc.save(f)

    # Format current date and time
    now = datetime.now()
    date_time = now.strftime("%m%d%Y_%H%M%S")  # Changed format to remove slashes and colons

    # Append date and time to the file name
    f.name = "Chat_History_" + date_time + '.docx'  # Changed to a static string "Chat_History_"
    f.seek(0)

    # Download button for chat history Word document
    st.download_button(
        label="Download chat history",
        data=f,
        file_name=f.name,
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
