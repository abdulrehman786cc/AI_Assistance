from openai import OpenAI
import speech_recognition as sr
import pyttsx3
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))# Replace with your actual API key

# Initialize recognizer and TTS
recognizer = sr.Recognizer()
tts = pyttsx3.init()

# Store user info
appointment_info = {
    "service": None,
    "name": None,
    "contact": None,
    "email": None,
    "date": None,
    "time": None,
    "datetime": None,
    "location": None
}

# GPT system role
chat_history = [
    {"role": "system", "content": "You are a helpful AI voice assistant that collects information to schedule an appointment. Please clean and convert responses into standard formats like YYYY-MM-DD for dates and 24-hour HH:MM for time."}
]

def speak(text):
    print(f"Assistant: {text}")
    tts.say(text)
    tts.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"🗣 You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn’t catch that. Can you repeat?")
            return None

def get_chatgpt_response(prompt):
    chat_history.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history
    )
    reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply.strip()

def collect_field(field_name, prompt):
    speak(prompt)
    while not appointment_info.get(field_name):
        response = listen()
        if response:
            appointment_info[field_name] = response

# --- Collect Scheduling Information ---

collect_field("service", "What service do you need? For example, cleaning or plumbing.")
collect_field("name", "May I have your full name?")
collect_field("contact", "What is your contact number?")
collect_field("email", "What is your email address?")

# Ask for date separately
while not appointment_info.get("date"):
    speak("What date would you prefer for the appointment?")
    response = listen()
    if response:
        gpt_date = get_chatgpt_response(f"Convert this to 'YYYY-MM-DD' format: '{response}'")
        appointment_info["date"] = gpt_date

# Ask for time separately
while not appointment_info.get("time"):
    speak("What time would you prefer?")
    response = listen()
    if response:
        gpt_time = get_chatgpt_response(f"Convert this to 24-hour 'HH:MM' format: '{response}'")
        appointment_info["time"] = gpt_time

# Combine date and time
appointment_info["datetime"] = f"{appointment_info['date']} {appointment_info['time']}"

# Optional location
collect_field("location", "Would you like to provide your location?")

# Final confirmation
speak("Thank you! I’ve collected your appointment information.")
print("\n✅ Appointment Information:")
print(json.dumps(appointment_info, indent=2))

# Step 1: Tell current time
current_time = datetime.now().strftime("%I:%M %p")
speak(f"The current time is {current_time}. Please tell me a suitable 3-hour time window for your service.")

# Step 2: Listen and store time window
time_window = None
while not time_window:
    response = listen()
    if response:
        time_window = response
        appointment_info["time_window"] = time_window

# Step 3: Thank the user
speak(f"Thank you! We've recorded your preferred time window as {time_window}. We’ll send you a confirmation shortly.")

