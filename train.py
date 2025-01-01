import google.generativeai as genai
from googletrans import Translator
from gtts import gTTS
import pygame
import os
import tkinter as tk
from tkinter import PhotoImage
import speech_recognition as sr
import io
import time
import threading

# Configure the generative AI model
api_key = "Add your API key"  # Replace with your actual Gemini API key
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Pygame mixer for audio playback
pygame.mixer.init()

# List of Indian languages and their corresponding ISO codes
indian_languages = {
    "Hindi": "hi",
    "English": "en",
    "Telugu": "te",
    "Tamil": "ta",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Odia": "or",
    "Bengali": "bn",
    "Assamese": "as",
    "Punjabi": "pa",
    "Urdu": "ur",
}

# Supported languages in gTTS
supported_languages = ['en', 'hi', 'ta', 'mr', 'gu', 'kn', 'ml', 'bn', 'pa', 'ur', 'or']

# Task management system
tasks = []
reminders = {}

def translate_chatbot_response(prompt, target_language):
    """
    Fetches a response from the Gemini chatbot, translates it to the target language,
    and returns the translated text.
    """
    response = model.generate_content(prompt).text
    translator = Translator()
    translated_text = translator.translate(response, dest=target_language).text
    return translated_text

def text_to_speech(text, language):
    """Convert text to speech and play it."""
    if language not in supported_languages:
        language = 'en'  # Fallback to English

    tts = gTTS(text=text, lang=language)
    audio_file = "temp_audio.mp3"
    tts.save(audio_file)

    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    os.remove(audio_file)

def update_output(text, language='en'):
    """Update both text and speech output."""
    result_label.config(text=text)  # Update text output on the GUI
    text_to_speech(text, language)  # Convert text to speech

def on_submit():
    prompt = entry.get()
    target_language = indian_languages.get(language_var.get(), 'en')

    # Get the translated chatbot response
    translated_response = translate_chatbot_response(prompt, target_language)

    # Update both text and speech output
    update_output(translated_response, target_language)

def on_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        result_label.config(text="Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio)
            entry.delete(0, tk.END)
            entry.insert(0, query)
            result_label.config(text="Voice input received. Press Submit to process.")
        except sr.UnknownValueError:
            result_label.config(text="Could not understand your speech. Please try again.")
        except sr.RequestError:
            result_label.config(text="Error with the speech recognition service.")
        except sr.WaitTimeoutError:
            result_label.config(text="Listening timed out. Please try again.")

def add_task():
    task = task_entry.get()
    if task:
        tasks.append(task)
        task_listbox.insert(tk.END, task)
        task_entry.delete(0, tk.END)
        # Update both text and speech output for task addition
        update_output(f"Task '{task}' added successfully!", 'en')
    else:
        update_output("Please enter a task.", 'en')

def delete_task():
    try:
        selected_task_index = task_listbox.curselection()[0]
        task = tasks[selected_task_index]
        task_listbox.delete(selected_task_index)
        tasks.pop(selected_task_index)
        # Update both text and speech output for task deletion
        update_output(f"Task '{task}' deleted successfully!", 'en')
    except IndexError:
        update_output("Please select a task to delete.", 'en')

def clear_input():
    entry.delete(0, tk.END)
    result_label.config(text="")

def set_reminder():
    task_index = task_listbox.curselection()
    if task_index:
        task_name = tasks[task_index[0]]
        reminder_time = reminder_entry.get()

        try:
            reminder_time = int(reminder_time)
            reminders[task_name] = reminder_time
            result_label.config(text=f"Reminder set for {task_name} in {reminder_time} seconds.")
            reminder_entry.delete(0, tk.END)

            # Update both text and speech output for reminder setting
            update_output(f"Reminder set for {task_name} in {reminder_time} seconds.", 'en')

            threading.Thread(target=reminder_notification, args=(task_name, reminder_time)).start()
        except ValueError:
            update_output("Please enter a valid reminder time (in seconds).", 'en')
    else:
        update_output("Please select a task to set a reminder.", 'en')

def reminder_notification(task_name, reminder_time):
    time.sleep(reminder_time)
    result_label.config(text=f"Reminder: {task_name} is due!")
    # Update both text and speech output for reminder notification
    update_output(f"Reminder: {task_name} is due!", 'en')

# Create the main window
window = tk.Tk()
window.title("Chatbot Translator with Audio and Task Management")
window.geometry("800x500")
window.configure(bg="#f0f0f0")

# Left Frame Widgets
left_frame = tk.Frame(window, bg="#f0f0f0")
left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

label = tk.Label(left_frame, text="Enter your query:", bg="#4CAF50", fg="white", font=("Arial", 12))
label.pack(pady=10)

entry = tk.Entry(left_frame, width=50, font=("Arial", 12))
entry.pack(pady=10)

language_var = tk.StringVar()
language_var.set("Select Language")
language_menu = tk.OptionMenu(left_frame, language_var, *indian_languages.keys())
language_menu.pack(pady=10)

submit_button = tk.Button(left_frame, text="Submit", command=on_submit, bg="#2196F3", fg="white", font=("Arial", 12))
submit_button.pack(pady=10)

voice_button = tk.Button(left_frame, text="Voice Input", command=on_voice_input, bg="#2196F3", fg="white",
                         font=("Arial", 12))
voice_button.pack(pady=10)

clear_button = tk.Button(left_frame, text="Clear", command=clear_input, bg="#f44336", fg="white", font=("Arial", 12))
clear_button.pack(pady=10)

result_label = tk.Label(left_frame, text="", wraplength=500, bg="#ffffff", font=("Arial", 10))
result_label.pack(pady=20)

# Right Frame Widgets
right_frame = tk.Frame(window, bg="#f0f0f0")
right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

task_label = tk.Label(right_frame, text="Manage Tasks:", bg="#4CAF50", fg="white", font=("Arial", 12))
task_label.pack(pady=10)

task_entry = tk.Entry(right_frame, width=50, font=("Arial", 12))
task_entry.pack(pady=10)

add_task_button = tk.Button(right_frame, text="Add Task", command=add_task, bg="#4CAF50", fg="white",
                            font=("Arial", 12))
add_task_button.pack(pady=10)

task_listbox = tk.Listbox(right_frame, width=50, height=5, font=("Arial", 12))
task_listbox.pack(pady=10)

delete_task_button = tk.Button(right_frame, text="Delete Task", command=delete_task, bg="#f44336", fg="white",
                               font=("Arial", 12))
delete_task_button.pack(pady=10)

reminder_label = tk.Label(right_frame, text="Set Reminder (seconds):", bg="#4CAF50", fg="white", font=("Arial", 12))
reminder_label.pack(pady=10)

reminder_entry = tk.Entry(right_frame, width=50, font=("Arial", 12))
reminder_entry.pack(pady=10)

set_reminder_button = tk.Button(right_frame, text="Set Reminder", command=set_reminder, bg="#2196F3", fg="white",
                                font=("Arial", 12))
set_reminder_button.pack(pady=10)

# Configure grid weight
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)

# Start the GUI loop
window.mainloop()
