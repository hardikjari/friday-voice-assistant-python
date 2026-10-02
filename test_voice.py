import pyttsx3
import time

def speak(text):
    print("Bot:", text)

    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()

    # time.sleep(0.5)

    engine.stop()

speak("Initializing Friday")

# time.sleep(2)

speak("Ya")

# time.sleep(2)

speak("Friday active")