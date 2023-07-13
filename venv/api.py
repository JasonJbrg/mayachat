import openai
from flask import Flask, request, jsonify
from translate import Translator
from pydub import AudioSegment
from pydub.playback import play
from datetime import datetime

app = Flask(__name__)

# Initialize the Translator
translator = Translator(to_lang="en", from_lang="ar")

# Define the tasks and their initial contexts
task_selection = config["task_selection"]
initial_context = {
    task: f"{config['initial_context'][task]} Please provide brief and concise responses."
    for task in task_selection
}

# Define the /chat endpoint
@app.route("/chat", methods=["POST"])
def chat_api():
    # Get the user input and selected task from the request
    user_input = request.json["user_input"]
    selected_task = request.json["selected_task"]

    # Load specific words from tcv.txt file
    with open("/Users/jasons/PycharmProjects/pythonProject/venv/tcv.txt", "r", encoding="utf-8") as file:
        specific_words = [word.strip() for word in file.readlines()]

    # Check if user's input has any of the specific words
    # If yes, play ding sound
    user_input_words = user_input.split()
    matching_words = set(specific_words).intersection(user_input_words)
    if matching_words:
        ding_sound_path = "/Users/jasons/PycharmProjects/pythonProject/venv/audio/tcv_match.mp3"
        ding_sound = AudioSegment.from_file(ding_sound_path)
        play(ding_sound)

    MAX_TOKENS = 500
    MAX_TOKENS_PER_MESSAGE = 50

    # Prepare the conversation for the chat model
    conversation = [
        {"role": "assistant", "content": initial_context[selected_task]},
        {"role": "user", "content": user_input}
    ]

    # Implement the chat logic using OpenAI API
    # You might need to adjust this part depending on your application logic
    return_openai = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=MAX_TOKENS,
        n=1
    )

    # Get assistant's response
    assistant_response = return_openai['choices'][0]['message']['content']

    # Return the response
    return jsonify({"response": assistant_response})


if __name__ == "__main__":
    app.run()
