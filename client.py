import requests
import speech_recognition as sr
from gtts import gTTS
import playsound
import os
import subprocess
from googlesearch import search

# API URL for your FastAPI server
API_URL = "http://raspi.lan:8000/generate"  # Replace <your-pi-ip> with your Raspberry Pi's IP address or hostname

# Initialize speech recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

def speak_text(text):
    """
    Speak the given text using Google TTS.
    """
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts_file = "response.mp3"
        tts.save(tts_file)
        playsound.playsound(tts_file, True)
        os.remove(tts_file)
    except Exception as e:
        print(f"Error in TTS: {e}")

def get_user_input():
    """
    Listen to the user's voice input and return it as text.
    """
    try:
        print("Listening for your command...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        # Recognize speech using Google Speech Recognition
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command

    except sr.UnknownValueError:
        print("Sorry, I couldn't understand you. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def send_to_server(prompt):
    """
    Send the user's input to the API server and return the response.
    """
    try:
        response = requests.post(API_URL, json={"prompt": prompt})
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "I'm sorry, I didn't understand that.")
        else:
            print(f"Server error: {response.status_code} - {response.text}")
            return "Sorry, there was a problem with the server."
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return "Unable to connect to the server."

def perform_google_search(query):
    """
    Perform a Google search and return the top results.
    """
    try:
        print(f"Searching Google for: {query}")
        results = []
        for result in search(query, num_results=3):
            results.append(result)
        return results
    except Exception as e:
        print(f"Error performing Google search: {e}")
        return ["I couldn't complete the search."]

def interact_with_system(command):
    """
    Execute basic system commands.
    """
    try:
        if "list files" in command:
            files = os.listdir(".")
            return f"Here are the files in the current directory: {', '.join(files)}"
        elif "open" in command:
            app = command.replace("open ", "").strip()
            subprocess.run(["xdg-open", app], check=True)
            return f"Opening {app}."
        elif "system info" in command:
            info = subprocess.check_output(["uname", "-a"], text=True)
            return f"Here is your system info: {info}"
        else:
            return "Sorry, I didn't recognize that system command."
    except Exception as e:
        print(f"Error interacting with system: {e}")
        return "There was an error executing the system command."

def main():
    """
    Main loop for the voice-enabled client.
    """
    print("Toxikun Voice Assistant is running. Say 'Toxic' to wake her up.")
    while True:
        print("Listening for the wake word 'Toxic'...")
        try:
            # Listen for the wake word
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            # Recognize speech for the wake word
            wake_word = recognizer.recognize_google(audio).lower()
            if "toxic" in wake_word:
                print("Wake word detected. How can I help you?")
                user_input = get_user_input()

                if user_input:
                    if "search for" in user_input:
                        query = user_input.replace("search for", "").strip()
                        search_results = perform_google_search(query)
                        response_text = f"Here are the top results: {'; '.join(search_results)}"
                    elif "system" in user_input or "files" in user_input or "open" in user_input:
                        response_text = interact_with_system(user_input)
                    else:
                        # Send input to the server and get response
                        response_text = send_to_server(user_input)

                    print(f"Toxikun: {response_text}")
                    speak_text(response_text)

        except sr.UnknownValueError:
            # If no valid speech is detected, continue listening
            pass
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

if __name__ == "__main__":
    main()
