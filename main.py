import pyttsx3
import speech_recognition as sr
import datetime
import os
import random
import requests
import wikipedia
import webbrowser
import urllib.parse
import pywhatkit as kit
import smtplib
from email.message import EmailMessage
import cohere
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
from PIL import Image, ImageTk
import threading
import time
import google.generativeai as genai
from gtts import gTTS
from playsound import playsound
import api

engine = pyttsx3.init('sapi5')
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 175)

chatStr = ""
is_listening = False

cohere_client = cohere.Client(api.cohere_key)
genai.configure(api_key=api.genai)

def speak(text):
    print(f"[SPEAK] {text}")
    try:
        tts = gTTS(text=text, lang='en')
        filename = "voice.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"[TTS Error - gTTS fallback] {e}")
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as ex:
            print(f"[TTS Error - pyttsx3] {ex}")

def append_log(text, speaker="system"):
    tag_styles = {
        "user": {"foreground": "#0066CC"},
        "assistant": {"foreground": "#006600"},
        "system": {"foreground": "#666666", "font": ("Arial", 9, "italic")}
    }
    log_area.tag_config(speaker, **tag_styles.get(speaker, {}))
    log_area.insert(tk.END, text + '\n', speaker)
    log_area.yview(tk.END)

def update_status(status_text):
    status_label.config(text=status_text)
    status_colors = {
        "Ready": "#4CAF50",
        "Listening": "#2196F3",
        "Processing": "#FFC107",
        "Analyzing": "#FFC107"
    }
    status_indicator.itemconfig(1, fill=status_colors.get(status_text, "#F44336"))
    root.update()

def Takecommand(timeout):
    global is_listening
    is_listening = True
    update_status("Listening")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        append_log("Listening...", "system")
        recognizer.pause_threshold = 1
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            update_status("Ready")
            return 'none'
    try:
        update_status("Recognizing")
        query = recognizer.recognize_google(audio, language='en-in')
        append_log(f"User: {query}", "user")
        return query
    except:
        return 'none'
    finally:
        is_listening = False
        update_status("Ready")

def chat(query):
    global chatStr
    update_status("Processing")
    append_log("Thinking...", "system")

    history = []
    for q in chatStr.strip().split("\n"):
        if q.strip():
            role = "USER" if "User:" in q else "CHATBOT"
            content = q.split(":", 1)[1].strip() if ":" in q else q.strip()
            if content:
                history.append({"role": role, "message": content})
    try:
        response = cohere_client.chat(
            message=query,
            model="command-r-plus",
            temperature=0.7,
            chat_history=history
        )
        answer = response.text.strip()
        print(f"[DEBUG] Raw answer: {repr(answer)}")
        spoken_answer = answer.replace("\n", "... ").strip()
        print(f"[SPEAK FUNCTION CALLED] Text to speak: {spoken_answer}")
        if spoken_answer:
            speak(spoken_answer)
            chatStr += f"User: {query}\nFraday: {spoken_answer}\n"
            append_log(answer, "assistant")  
        else:
            speak("Sorry, I didn't get that.")
            append_log("No response from assistant.", "system")
    except Exception as e:
        append_log(f"Error: {e}", "system")
        speak("Sorry, I couldn't complete that.")
    finally:
        update_status("Ready")

def update_status(status_text):
    status_label.config(text=status_text)
    root.update()  

def wish():
    hour = int(datetime.datetime.now().hour)
    if 5 <= hour < 12:
        greet = "Good morning"
    elif 12 <= hour < 18:
        greet = "Good afternoon"
    else:
        greet = "Good evening"
    speak(f"{greet}, sir! I am Fraday, your assistant. Please tell me how I can help you.")

def process_command():
    query = text_var.get().lower().strip()
    if not query:
        return
    text_var.set("")
    append_log(f"User: {query}", "user")
    update_status("Processing...")
    threading.Thread(target=process_command_thread, args=(query,), daemon=True).start()

def process_command_thread(query):
    if 'exit' in query or 'quit' in query or 'goodbye' in query or 'bye' in query:
        speak('Goodbye! Have a great day!')
        time.sleep(2)  
        root.quit()
        return
    elif 'classify image' in query or 'identify image' in query or 'what is in this image' in query:
        classify_image()
    elif 'play song on youtube' in query.lower():
        play_song_on_youtube()
    elif 'open notepad' in query:
        os.startfile("C:\\Windows\\system32\\notepad.exe")
    elif 'open command prompt' in query:
        os.system('start cmd')
    elif 'open ms word' in query:
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.exe")#Your Path
    elif 'open ms excel' in query:
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.exe")#Your Path
    elif 'open ms powerpoint' in query:
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.exe")#Your Path
    elif 'open google chrome' in query:
        os.startfile("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe")#Your Path
    elif 'open keyboard' in query:
        os.startfile("C:\\Windows\\system32\\osk.exe")#Your Path
    elif 'open minecraft' in query:
        os.startfile("C:\\Users\\ACS\\AppData\\Roaming\\.minecraft\\TLauncher.exe")#Your Path
    elif 'open roblox' in query:
        os.startfile("C:\\Users\\ACS\\AppData\\Local\\Roblox\\Versions\\version-86c3597a87f4495e\\RobloxPlayerBeta.exe")#Your Path
    elif 'open calculator' in query:
        os.startfile("D:\\faaiz work\\python\\claculaTor\\dist\\maincalculator.exe")#Your Path
    elif 'open flappy bird' in query:
        os.startfile("D:\\faaiz work\\python\\flappy bird\\dist\\flappybird.exe")#Your Path
    elif 'play music' in query:
        mupath = "D:\\music"#Your Path
        songs = os.listdir(mupath)
        rd = random.choice(songs)
        os.startfile(os.path.join(mupath, rd))
    elif 'ip address' in query:
        ip = requests.get('https://api.ipify.org').text
        speak(f'Your IP address is {ip}')
    elif 'wikipedia' in query:
        speak('Searching Wikipedia...')
        query = query.replace('wikipedia', '')
        result = wikipedia.summary(query, sentences=2)
        speak(f'According to Wikipedia: {result}')
    elif 'open youtube' in query:
        webbrowser.open('https://www.youtube.com')
    elif 'open facebook' in query:
        webbrowser.open('https://www.facebook.com')
    elif 'open instagram' in query:
        webbrowser.open('https://www.instagram.com')
    elif 'open chat gpt' in query:
        webbrowser.open('https://www.chatgpt.com')
    elif 'open google' in query:
        speak('What should I search on Google?')
        cm = Takecommand(timeout=5).lower()
        search_url = f'https://www.google.com/search?q={urllib.parse.quote(cm)}'
        webbrowser.open(search_url)
    elif 'send message' in query:
        send_whatsapp_message()
    elif 'send email' in query:
        handle_send_email()
    elif 'weather' in query and 'city' in query:
        city = query.split('in')[-1].strip()
        get_weather(city)
    elif 'weather' in query:
        speak("Which city's weather would you like to know?")
        start_voice_recognition_for_weather()
        return
    elif 'news' in query and 'about' in query:
        topic = query.split('about')[-1].strip()
        get_news(topic)
    elif 'news' in query:
        speak("What topic do you want the latest news about?")
        start_voice_recognition_for_news()
        return
    elif 'calculate' in query:
        calculation = query.replace('calculate', '').strip()
        if calculation:
            calculate(calculation)
        else:
            speak("What calculation would you like to perform?")
            start_voice_recognition_for_calculation()
            return
    elif 'reset chat' in query:
        handle_reset_chat()
    elif 'time' in query:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}")
    elif 'date' in query:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {current_date}")
    else:
        chat(query)
    update_status("Ready")
    speak('Do you have any other requests?')

def classify_image():
    update_status("Selecting image...")
    speak("Please select an image to classify.")
    def open_file_dialog():
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            display_selected_image(file_path)
            ask_about_image(file_path)
        else:
            speak("No image selected.")
            update_status("Ready")
    root.after(0, open_file_dialog)

def display_selected_image(image_path):
    try:
        if not hasattr(root, 'image_frame'):
            root.image_frame = tk.Frame(main_frame, bg="#f0f0f0")
            root.image_frame.pack(fill=tk.X, pady=10, before=log_frame)
            root.image_label = tk.Label(root.image_frame, bg="#ffffff", bd=2, relief=tk.GROOVE)
            root.image_label.pack(padx=10, pady=10)
        else:
            root.image_frame.pack(fill=tk.X, pady=10, before=log_frame)
        img = Image.open(image_path)
        max_width, max_height = 300, 250
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width/width, max_height/height)
            width = int(width * ratio)
            height = int(height * ratio)
            img = img.resize((width, height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        root.image_label.config(image=photo)
        root.image_label.image = photo  
        append_log(f"Image loaded: {os.path.basename(image_path)}", "system")
    except Exception as e:
        append_log(f"Error displaying image: {str(e)}", "system")

def ask_about_image(image_path):
    query_dialog = tk.Toplevel(root)
    query_dialog.title("Image Analysis")
    query_dialog.geometry("400x300")
    query_dialog.transient(root)
    query_dialog.grab_set()
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    query_dialog.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    tk.Label(
        query_dialog, 
        text="What would you like to know about this image?",
        font=("Arial", 12, "bold"),
        pady=10
    ).pack()
    questions_frame = tk.Frame(query_dialog)
    questions_frame.pack(pady=10, fill=tk.X)
    questions = [
        "What is this?",
        "Describe briefly",
        "Count objects",
        "Identify colors",
        "Custom question..."
    ]
    
    def on_question_click(question):
        if question == "Custom question...":
            custom_question = custom_entry.get().strip()
            if custom_question:
                query_dialog.destroy()
                analyze_image_with_question(image_path, custom_question)
        else:
            query_dialog.destroy()
            analyze_image_with_question(image_path, question)
    for i, question in enumerate(questions[:-1]):
        btn = tk.Button(
            questions_frame,
            text=question,
            command=lambda q=question: on_question_click(q),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10),
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=5,
            width=15
        )
        btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="ew")
    
    custom_frame = tk.Frame(query_dialog)
    custom_frame.pack(pady=10, fill=tk.X, padx=20)
    
    custom_entry = tk.Entry(
        custom_frame,
        font=("Arial", 11),
        relief=tk.GROOVE,
        bd=2
    )
    custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    custom_btn = tk.Button(
        custom_frame,
        text="Ask",
        command=lambda: on_question_click("Custom question..."),
        bg="#2196F3",
        fg="white",
        font=("Arial", 10),
        relief=tk.RAISED,
        bd=2
    )
    custom_btn.pack(side=tk.RIGHT)
    tk.Button(
        query_dialog,
        text="Cancel",
        command=query_dialog.destroy,
        bg="#f44336",
        fg="white",
        font=("Arial", 10),
        relief=tk.RAISED,
        bd=2,
        padx=10,
        pady=5
    ).pack(pady=10)

def analyze_image_with_question(image_path, question):
    update_status("Analyzing image...")
    speak(f"Analyzing the image to {question.lower()}. This may take a moment.")
    try:
        myfile = genai.upload_file(image_path)
        model = genai.GenerativeModel("gemini-1.5-flash")
        if question == "What is this?":
            prompt = "Identify the main subject of this image in a single short sentence (15 words or less).Answer concisely in 1-2 lines"
        elif question == "Describe briefly":
            prompt = "Give a brief 1-2 sentence description of this image.Answer concisely in 1-2 lines"
        elif question == "Count objects":
            prompt = "Count and list the main objects visible in this image in a concise bullet-point format.Just provide the count of objects without any additional text."
        elif question == "Identify colors":
            prompt = "List the main colors present in this image in order of dominance.Just provide the colors without any additional text."
        else:
            prompt = f"{question} Answer concisely in 1-2 lines."
        
        result = model.generate_content([myfile, prompt])
        analysis_text = result.text
        speak("Here's what I found.")
        speak(analysis_text)
        append_log(f"Image Analysis ({question}): {analysis_text}", "assistant")
        display_analysis_results(question, analysis_text, image_path)
    except Exception as e:
        error_message = f"Error analyzing image: {str(e)}"
        speak("Sorry, I encountered an error while analyzing the image.")
        append_log(error_message, "system")
    update_status("Ready")

def display_analysis_results(question, analysis_text, image_path=None):
    results_dialog = tk.Toplevel(root)
    results_dialog.title("Analysis Results")
    results_dialog.geometry("450x400")
    results_dialog.transient(root)
    window_width = 450
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    results_dialog.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    tk.Label(
        results_dialog, 
        text=f"Question: {question}",
        font=("Arial", 12, "bold"),
        pady=10
    ).pack(fill=tk.X, padx=20)
    result_text = scrolledtext.ScrolledText(
        results_dialog,
        wrap=tk.WORD,
        font=("Arial", 11),
        height=10,
        bg="#ffffff",
        fg="#333333"
    )
    result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    result_text.insert(tk.END, analysis_text)
    result_text.config(state=tk.DISABLED)
    buttons_frame = tk.Frame(results_dialog)
    buttons_frame.pack(fill=tk.X, padx=20, pady=10)
    if image_path:
        tk.Button(
            buttons_frame,
            text="Ask Another Question",
            command=lambda: (results_dialog.destroy(), ask_about_image(image_path)),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10),
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    tk.Button(
        buttons_frame,
        text="Close",
        command=results_dialog.destroy,
        bg="#f44336",
        fg="white",
        font=("Arial", 10),
        relief=tk.RAISED,
        bd=2,
        padx=10,
        pady=5
    ).pack(side=tk.RIGHT, padx=5)

def start_voice_recognition():
    if is_listening:
        return
    voice_button.config(state=tk.DISABLED)
    threading.Thread(target=voice_recognition_thread, daemon=True).start()

def voice_recognition_thread():
    query = Takecommand(timeout=5).lower()
    if query != 'none':
        text_var.set(query)
        process_command()
    voice_button.config(state=tk.NORMAL)

def start_voice_recognition_for_search():
    update_status("Listening for search query...")
    threading.Thread(target=google_search_thread, daemon=True).start()

def google_search_thread():
    cm = Takecommand(timeout=10).lower()
    if cm != 'none':
        update_status("Searching Google...")
        append_log(f"Searching Google for: {cm}", "system")
        search_url = f'https://www.google.com/search?q={urllib.parse.quote(cm)}'
        webbrowser.open(search_url)
        speak(f"Here are the search results for {cm}")
    else:
        speak("I didn't catch that. Please try your search again.")
    update_status("Ready")
    speak('Do you have any other requests?')

def start_voice_recognition_for_weather():
    update_status("Listening for city name...")
    threading.Thread(target=weather_thread, daemon=True).start()

def weather_thread():
    city = Takecommand(timeout=10).lower()
    if city != 'none':
        get_weather(city)
    else:
        speak("I didn't catch the city name. Please try again.")
    update_status("Ready")
    speak('Do you have any other requests?')

def start_voice_recognition_for_news():
    update_status("Listening for news topic...")
    threading.Thread(target=news_thread, daemon=True).start()

def news_thread():
    topic = Takecommand(timeout=10).lower()
    if topic != 'none':
        get_news(topic)
    else:
        speak("I didn't catch the topic. Please try again.")
    update_status("Ready")
    speak('Do you have any other requests?')

def start_voice_recognition_for_calculation():
    update_status("Listening for calculation...")
    threading.Thread(target=calculation_thread, daemon=True).start()

def calculation_thread():
    calculation_query = Takecommand(timeout=15).lower()
    if calculation_query != 'none':
        calculate(calculation_query)
    else:
        speak("I didn't catch the calculation. Please try again.")
    update_status("Ready")
    speak('Do you have any other requests?')

def send_whatsapp_message():
    speak("Please tell me the phone number without the country code.")
    phone_number = Takecommand(timeout=10).strip()
    if phone_number == 'none':
        speak("I didn't get the phone number. Please try again.")
        return
    speak("What message would you like to send?")
    message = Takecommand(timeout=15).strip()
    if message == 'none':
        speak("I didn't get the message. Please try again.")
        return
    country_code = '+92'
    full_phone_number = country_code + phone_number
    try:
        update_status("Sending WhatsApp message...")
        kit.sendwhatmsg_instantly(full_phone_number, message)
        speak(f"Message sent to {full_phone_number}")
    except Exception as e:
        speak(f"Sorry, I couldn't send the message. Error: {str(e)}")

def play_song_on_youtube():
    speak("What song would you like to play?")
    song_name = Takecommand(timeout=15).strip() 
    if song_name == 'none':
        speak("I didn't get the song name. Please try again.")
        return
    update_status(f"Playing {song_name} on YouTube...")
    speak(f"Playing {song_name} on YouTube.")
    kit.playonyt(song_name)

def send_email(to, content):
    email_address = api.email  
    email_password = api.password  
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = 'Message from Python Assistant'
    msg['From'] = email_address
    msg['To'] = to

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
            return True
    except Exception as e:
        print(e)
        return False

def handle_send_email():
    speak("Please tell me the recipient's email address.")
    to = Takecommand(timeout=15).strip()
    if to == 'none':
        speak("I didn't get the email address. Please try again.")
        return
    speak("What should I write in the email?")
    content = Takecommand(timeout=20).strip()
    if content == 'none':
        speak("I didn't get the email content. Please try again.")
        return
    if send_email(to, content):
        speak(f"Email has been sent to {to}.")
    else:
        speak("Sorry, I couldn't send the email.")

def get_weather(city):
    API_KEY = api.weather  
    try:
        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric')
        data = response.json()
        if data['cod'] == 200:
            temperature = data['main']['temp']
            weather = data['weather'][0]['description']
            speak(f"The current temperature in {city} is {temperature}°C with {weather}.")
        else:
            speak("Sorry, I couldn't find the weather information for that city.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")

def get_news(topic):
    API_KEY = api.news  
    try:
        response = requests.get(f'https://newsapi.org/v2/everything?q={topic}&apiKey={API_KEY}')
        data = response.json()
        if data['status'] == 'ok':
            articles = data['articles'][:1]
            for article in articles:
                title = article['title']
                description = article['description']
                speak(f"Title: {title}. Description: {description}.")
        else:
            speak("Sorry, I couldn't find any news about that topic.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")

def calculate(calculation_query):
    try:
        result = eval(calculation_query)
        speak(f"The result is {result}.")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")

def handle_reset_chat():
    global chatStr
    chatStr = ""
    speak("Chat history has been reset.")

root = tk.Tk()
root.title("Fraday Voice Assistant")
root.configure(bg="#f5f5f7")  
root.option_add("*Font", "Arial 10")
root.option_add("*Button.Relief", "flat")

main_frame = tk.Frame(root, bg="#f5f5f7", padx=20, pady=15)
main_frame.pack(fill=tk.BOTH, expand=True)

title_label = tk.Label(
    main_frame, 
    text="Fraday Voice Assistant", 
    font=("Arial", 16, "bold"), 
    bg="#f0f0f0",
    fg="#333333"
)
title_label.pack(pady=10)

input_frame = tk.Frame(main_frame, bg="#f5f5f7")
input_frame.pack(fill=tk.X, pady=5)

text_var = tk.StringVar()
text_input_frame = tk.Frame(input_frame, bg="#e1e1e6", bd=0, highlightthickness=1, highlightbackground="#cccccc", highlightcolor="#4285F4")
text_input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

text_input = tk.Entry(
    text_input_frame, 
    textvariable=text_var, 
    font=("Arial", 11),
    bd=0,
    bg="#e1e1e6",
    insertbackground="#333333"  
)
text_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
text_input.bind("<Return>", lambda event: process_command())

send_button_frame = tk.Frame(input_frame, bg="#f5f5f7")
send_button_frame.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(
    send_button_frame,
    text="Send",
    command=process_command,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    bd=0,
    padx=15,
    pady=8,
    cursor="hand2"  
)
send_button.pack(fill=tk.BOTH, expand=True)

voice_button_frame = tk.Frame(input_frame, bg="#f5f5f7")
voice_button_frame.pack(side=tk.LEFT, padx=5)

voice_button = tk.Button(
    voice_button_frame,
    text="🎤 Speak",
    command=start_voice_recognition,
    bg="#2196F3",
    fg="white",
    font=("Arial", 10, "bold"),
    bd=0,
    padx=15,
    pady=8,
    cursor="hand2"
)
voice_button.pack(fill=tk.BOTH, expand=True)

image_button_frame = tk.Frame(input_frame, bg="#f5f5f7")
image_button_frame.pack(side=tk.LEFT, padx=5)

image_button = tk.Button(
    image_button_frame,
    text="📷 Image",
    command=classify_image,
    bg="#673AB7",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    padx=15,
    pady=8,
    cursor="hand2"
)
image_button.pack(fill=tk.BOTH, expand=True)

def on_enter(e, button, color):
    button['background'] = color

def on_leave(e, button, color):
    button['background'] = color

send_button.bind("<Enter>", lambda e: on_enter(e, send_button, "#45a049"))
send_button.bind("<Leave>", lambda e: on_leave(e, send_button, "#4CAF50"))

voice_button.bind("<Enter>", lambda e: on_enter(e, voice_button, "#0b7dda"))
voice_button.bind("<Leave>", lambda e: on_leave(e, voice_button, "#2196F3"))

image_button.bind("<Enter>", lambda e: on_enter(e, image_button, "#5e35b1"))
image_button.bind("<Leave>", lambda e: on_leave(e, image_button, "#673AB7"))

status_frame = tk.Frame(main_frame, bg="#f5f5f7")
status_frame.pack(fill=tk.X, pady=5)

status_indicator = tk.Canvas(status_frame, width=10, height=10, bg="#f5f5f7", highlightthickness=0)
status_indicator.pack(side=tk.LEFT, padx=(0, 5))
status_indicator.create_oval(0, 0, 10, 10, fill="#4CAF50", outline="")

status_label = tk.Label(
    status_frame, 
    text="Ready", 
    font=("Arial", 9),
    bg="#f5f5f7",
    fg="#555555"
)
status_label.pack(side=tk.LEFT)

def update_status(status_text):
    status_label.config(text=status_text)
    if status_text == "Ready":
        status_indicator.itemconfig(1, fill="#4CAF50")  
    elif "Listening" in status_text:
        status_indicator.itemconfig(1, fill="#2196F3")  
    elif "Processing" in status_text or "Analyzing" in status_text:
        status_indicator.itemconfig(1, fill="#FFC107")  
    else:
        status_indicator.itemconfig(1, fill="#F44336") 
    root.update()

log_frame = tk.Frame(main_frame, bg="white", bd=1, relief=tk.FLAT, highlightthickness=1, highlightbackground="#e0e0e0")
log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

log_area = scrolledtext.ScrolledText(
    log_frame, 
    wrap=tk.WORD, 
    font=("Arial", 10),
    bg="white",
    fg="#333333",
    bd=0,
    padx=5,
    pady=5
)
log_area.pack(fill=tk.BOTH, expand=True)
log_area.tag_config("user", foreground="#0066CC", font=("Arial", 10, "bold"))
log_area.tag_config("assistant", foreground="#006600")
log_area.tag_config("system", foreground="#666666", font=("Arial", 9, "italic"))

scrollbar = ttk.Scrollbar(log_area)
log_area.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=log_area.yview)

footer_frame = tk.Frame(main_frame, bg="#f5f5f7")
footer_frame.pack(fill=tk.X, pady=5)

footer_label = tk.Label(
    footer_frame, 
    text="© 2023 Fraday Voice Assistant", 
    font=("Segoe UI", 8),
    bg="#f5f5f7",
    fg="#777777"
)
footer_label.pack(side=tk.RIGHT)

text_input.focus_set()
window_width = 700
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

if __name__ == "__main__":
    text_input.focus_set()
    root.geometry(f"{700}x{600}+{(root.winfo_screenwidth() - 700) // 2}+{(root.winfo_screenheight() - 600) // 2}")
    wish()  
    update_status("Ready")
    root.mainloop()
