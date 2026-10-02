import speech_recognition as sr
import difflib
import webbrowser
import pyttsx3
import time
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import threading

newsapikey = "Your_NewsData_API_Key_Here"  # Replace with your actual NewsData API key
pygame.init()
pygame.mixer.init()
stop_speech_event = threading.Event()
shutdown_event = threading.Event()

def speak_old(text):
    print("Bot:", text)

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for voice in voices:
        if "zira" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()
    engine.stop()


def speak(text):
    print("Bot:", text)

    stop_speech_event.clear()

    recognizer = sr.Recognizer()

    # Start listening for "stop Friday"
    stop_listener = recognizer.listen_in_background(
        sr.Microphone(),
        stop_listener_callback,
        phrase_time_limit=2
    )

    try:
        # Create TTS file
        tts = gTTS(text=text, lang="en")
        tts.save("temp.mp3")

        # Load and play immediately
        pygame.mixer.music.load("temp.mp3")
        pygame.mixer.music.play()

        # Wait until speech finishes
        while pygame.mixer.music.get_busy():
            # Stop if "stop Friday" was detected
            if stop_speech_event.is_set():
                pygame.mixer.music.stop()
                break

            time.sleep(0.05)

            # Release the file
        try:
                pygame.mixer.music.unload()
        except:
                pass

        if os.path.exists("temp.mp3"):
            os.remove("temp.mp3")

    except Exception as e:
        print("Speak Error:", e)

    finally:
        # Stop background microphone listener
        stop_listener(wait_for_stop=False)

def find_song(query, library):
    q = query.lower().strip(" .?!")
    q = q.replace("the song", "").replace("song", "").strip()
    q_no_spaces = q.replace(" ", "")

    # 1. Exact match (case-insensitive)
    for title, link in library.items():
        if title.lower() == q:
            return title, link

    # 2. Match without spaces (e.g. "a b c d e f u" -> "abcdefu")
    for title, link in library.items():
        if title.lower().replace(" ", "") == q_no_spaces:
            return title, link

    # 3. Substring match (e.g. "dua lipa levitating" or "play levitating song")
    for title, link in library.items():
        if title.lower() in q or (len(q) > 2 and q in title.lower()):
            return title, link

    # 4. Fuzzy match fallback
    matches = difflib.get_close_matches(q, library.keys(), n=1, cutoff=0.6)
    if matches:
        return matches[0], library[matches[0]]

    return None, None

def aiProcess(command):
    try:
        client = OpenAI(
            api_key="YOUR_OPENAI_API_KEY_HERE_PAID"  # Replace with your actual OpenAI API key
        )

        response = client.responses.create(
            model="gpt-5.6-luna",
            tools=[{"type": "web_search"}],
            input=f"""
                   Answer the following question briefly.

                    Rules:
                    - Maximum 2 sentences.
                    - Return plain text only.
                    - No Markdown.
                    - No asterisks.
                    - No bullet points.
                    - No headings.
                    - No code formatting.
                    - Speak naturally.
                    Question: {command}
                    """
        )

        return response.output_text

    except Exception as e:
        print(f"AI Error: {type(e).__name__} - {e}")
        return "Sorry boss, I am unable to process that request right now."

def stop_listener_callback(recognizer, audio):
    try:
        command = recognizer.recognize_google(audio).lower().strip()

        print("Background heard:", command)

        if "stop friday" in command or command == "stop":
            print("🛑 Stop command detected!")

            # Stop current speech immediately
            stop_speech_event.set()

            # Stop Friday completely
            shutdown_event.set()

            # Stop pygame audio
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

    except sr.UnknownValueError:
        pass

    except sr.RequestError:
        pass

    except Exception as e:
        print("Stop listener error:", e)

def processCommand(command):
    if "open google" in command.lower():
        webbrowser.open("https://google.com")
    elif "open youtube" in command.lower():
        webbrowser.open("https://youtube.com")
    elif "open instagram" in command.lower():
        webbrowser.open("https://instagram.com")
    elif "open linkedin" in command.lower():
        webbrowser.open("https://linkedin.com")
    elif command.lower().startswith("play"):
        # Get everything after "play"
        song = command[4:].strip()

        print("Song received:", song)

        if not song:
            speak("Please tell me which song to play.")
            return

        matched_title, link = find_song(song, musicLibrary.music)

        if link:
            print("Playing:", matched_title)
            print("Link:", link)

            webbrowser.open(link)
            speak(f"Playing {matched_title}")

        else:
            speak(f"I could not find {song} in your music library.")
            print("Available songs:", list(musicLibrary.music.keys()))

    elif "news" in command.lower():
        r = requests.get(f"https://newsdata.io/api/1/latest?apikey={newsapikey}&country=in&language=en")
        data = r.json()

        if data["status"] == "success":

            for article in data["results"][:10]:
                headline = article["title"]

                speak(headline)
        else:
            print("Failed to fetch news")
            speak("Sorry boss, I could not fetch the latest news.")
    

    else:
        # Let OpenAI to handle this request
        output = aiProcess(command)
        speak(output)



if __name__  ==  "__main__":
    speak("Initializing Friday...")
   
    while not shutdown_event.is_set():

        # Listen for the wake word 'hHi Friday!'
        # obtain audio from the microphone

        r = sr.Recognizer()

        # recognize speech using Sphinx
        print("Recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source,timeout=2,phrase_time_limit=1)

            word = r.recognize_google(audio)
            if(word.lower() == "friday"):
                speak("Yes boss!!")

                #Listen for command
                with sr.Microphone() as source:
                    print("Friday active...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)

                    processCommand(command)
                                                 
        except sr.UnknownValueError:
            print("Error: Could not understand the audio.")

        except sr.RequestError as e:
            print(f"Error: Could not connect to Google Speech Recognition. {e}")

        except Exception as e:
            print(f"Error :  {type(e).__name__} - {e}")
