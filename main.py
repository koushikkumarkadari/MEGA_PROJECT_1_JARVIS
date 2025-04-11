import speech_recognition as sr
import webbrowser
import pyttsx3
import music
import requests
import google.generativeai as genai
import os
from gtts import gTTS
import pygame
import time

genai.configure(api_key=os.environ["GEMINI_KEY"])
model=genai.GenerativeModel("gemini-1.5-flash-002")

recognizer = sr.Recognizer()
engine=pyttsx3.init()
voices = engine.getProperty('voices')       
engine.setProperty('voice', voices[1].id)

def speak_old(text):
    engine.say(text)
    engine.runAndWait()


def speak(text):
    # Convert text to speech and save as MP3
    tts = gTTS(text)
    tts.save("response.mp3")

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()  # Wait for the music to finish playing
    os.remove("response.mp3")
   

    # Optionally delete the file after playback
    


def processCommand(c):
    if "open youtube" in c.lower():
        speak("Opening Youtube")
        webbrowser.open("https://www.youtube.com/")
    elif "open google" in c.lower():
        speak("Opening Google")
        webbrowser.open("https://www.google.com/")
    elif "open stack overflow" in c.lower():
        speak("Opening Stack Overflow")
        webbrowser.open("https://stackoverflow.com/")
    elif "open github" in c.lower():
        speak("Opening Github")
        webbrowser.open("https://github.com/")
    elif c.startswith("play"):
        song_name = c.replace("play", "").strip()
        if song_name in music.music:
            speak(f"Playing {song_name}")
            webbrowser.open(music.music[song_name])
        else:
            speak("Song not found in the library.")
    elif "weather" in c.lower():
        speak("Please tell me the city name")
        with sr.Microphone() as source:
            print("Listening for city name...")
            audio = recognizer.listen(source)
            city_name = recognizer.recognize_google(audio)
            api_key = "4c73e1e488ec4cc395782845251104"
            base_url = f"http://api.weatherapi.com/v1/current.json?key={os.environ["WEATHER_KEY"]}&q={city_name}"
            response = requests.get(base_url)
            data = response.json()
            if "error" in data:
                speak("City not found.")
            else:
                temperature = data["current"]["temp_c"]
                condition = data["current"]["condition"]["text"]
                speak(f"The current temperature in {city_name} is {temperature} degrees Celsius with {condition}.")
    elif "headlines" in c.lower():
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={os.environ["NEWS_KEY"]}")
        news = r.json()
        articles = news["articles"]
        headlines = []
        for article in articles:
            headlines.append(article["title"])
        speak("Here are the top headlines:")
        for i, headline in enumerate(headlines):
            if i >= 5:
                break
            speak(f"Headline {i+1}: {headline}") 
    else:
        try:
            #let gemini handle the command
            speak("let me think...")
            response=model.generate_content(f"{c} .answer in only one sentence")
            speak(response.text)
        except Exception as e:
            print("Sorry, I did not understand that.")
            speak("Sorry, I did not understand that.")
   
if __name__ == "__main__":
    speak("Initializing friday....")
    while(True):
        #Listen for the wake word
        #obtain the microphone input
        r=sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio=r.listen(source,timeout=2,phrase_time_limit=2)
            word=r.recognize_google(audio)
            if("friday" in word.lower()):
                speak("Yes boss")
                #listen for command
                with sr.Microphone() as source:
                    print("Listening for command...")
                    audio=r.listen(source)
                    command=r.recognize_google(audio)

                    processCommand(command)
                    #print(command)
        except Exception as e:
            print("Sorry, I did not understand that.")
            
    