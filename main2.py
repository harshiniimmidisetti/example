import streamlit as st
import sqlite3
import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import speech_recognition as sr
import pyttsx3

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Beauty Plus", page_icon="✨", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    before_img TEXT,
    after_img TEXT)''')

conn.commit()

# ---------------- VOICE ----------------
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return "Couldn't understand"

# ---------------- FACE DETECTION ----------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
'haarcascade_frontalface_default.xml')

def detect_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)

    return image, len(faces)

# ---------------- SKIN TONE ----------------
def detect_skin_tone(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = img.reshape(-1, 3)

    sample = pixels[np.random.choice(pixels.shape[0], 5000, replace=False)]
    avg = np.mean(sample, axis=0)

    r,g,b = avg

    if r > 180 and g > 140:
        return "Fair"
    elif r > 140:
        return "Medium"
    else:
        return "Dark"

def skin_tone_style(tone):
    if tone == "Fair":
        return "Pastel, pink, sky blue 🌸"
    elif tone == "Medium":
        return "Orange, teal, yellow 🌈"
    else:
        return "White, royal blue, red 🔥"

# ---------------- STYLE ----------------
def get_style(face, occasion):
    if occasion == "Wedding":
        return "Elegant bun 💍", "Red, gold 👗"
    elif occasion == "Party":
        return "Loose curls 🎉", "Black, glitter ✨"
    elif occasion == "College":
        return "Simple ponytail 🎓", "Casual denim 💙"
    else:
        return "Braids 🌸", "Ethnic bright 🌈"

# ---------------- CHATBOT ----------------
def chatbot(msg):
    msg = msg.lower()
    if "sad" in msg:
        return "Take rest 💖"
    elif "happy" in msg:
        return "Keep shining ✨"
    elif "stress" in msg:
        return "Relax 🧘"
    else:
        return "I'm here for your glow-up ✨"

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- TITLE ----------------
st.title("✨ Beauty Plus Glow-Up Planner")

# ---------------- LOGIN ----------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Register"):
        c.execute("INSERT INTO users VALUES (NULL,?,?)",(u,p))
        conn.commit()
        st.success("Account created!")

elif choice == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))
        data = c.fetchone()
        if data:
            st.session_state.user = data
            st.success("Login success")

# ---------------- MAIN ----------------
if st.session_state.user:

    page = st.sidebar.selectbox("Options",["Dashboard","Style","Chatbot"])

    # -------- DASHBOARD --------
    if page == "Dashboard":
        st.subheader("📸 Upload / Camera")

        col1,col2 = st.columns(2)

        with col1:
            before = st.file_uploader("Before")
            after = st.file_uploader("After")

        with col2:
            cam = st.camera_input("Take Photo")

        if st.button("Save"):
            os.makedirs("uploads",exist_ok=True)

            if before:
                with open(f"uploads/{before.name}","wb") as f:
                    f.write(before.getbuffer())

            if after:
                with open(f"uploads/{after.name}","wb") as f:
                    f.write(after.getbuffer())

            if cam:
                img = Image.open(cam)
                img_np = np.array(img)
                img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                face_img, count = detect_face(img_cv)
                tone = detect_skin_tone(img_cv)

                st.image(face_img, caption=f"Faces: {count}")
                st.success(f"Skin Tone: {tone}")
                st.info(f"Best Colors: {skin_tone_style(tone)}")

            c.execute("INSERT INTO progress VALUES (NULL,?,?,?)",
                      (st.session_state.user[0],
                       before.name if before else "",
                       after.name if after else ""))
            conn.commit()

            st.success("Saved!")

        # -------- HISTORY --------
        st.subheader("📂 Your Progress")

        c.execute("SELECT * FROM progress WHERE user_id=?",
                  (st.session_state.user[0],))
        rows = c.fetchall()

        for r in rows:
            col1,col2 = st.columns(2)

            with col1:
                if r[2]:
                    st.image(f"uploads/{r[2]}", caption="Before")

            with col2:
                if r[3]:
                    st.image(f"uploads/{r[3]}", caption="After")

            st.divider()

        # -------- CHART --------
        st.subheader("📊 Glow-Up Progress")

        if rows:
            df = pd.DataFrame({
                "Step": list(range(1,len(rows)+1)),
                "Uploads":[1]*len(rows)
            })
            st.line_chart(df.set_index("Step"))

    # -------- STYLE --------
    elif page == "Style":
        face = st.selectbox("Face Shape",["oval","round","square"])
        occ = st.selectbox("Occasion",["Wedding","Party","College","Festival"])

        if st.button("Suggest"):
            h,o = get_style(face,occ)
            st.write("Hair:",h)
            st.write("Outfit:",o)

    # -------- CHATBOT --------
    elif page == "Chatbot":
        col1,col2 = st.columns(2)

        with col1:
            msg = st.text_input("Message")
            if st.button("Send"):
                reply = chatbot(msg)
                st.write("🤖",reply)
                speak(reply)

        with col2:
            if st.button("🎙 Speak"):
                text = listen()
                st.write("You:",text)
                reply = chatbot(text)
                st.write("🤖",reply)
                speak(reply)