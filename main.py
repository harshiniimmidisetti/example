import streamlit as st
import sqlite3
import os
import speech_recognition as sr
import pyttsx3

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Beauty Plus", page_icon="✨", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background: linear-gradient(to right, #f8f9fa, #e3f2fd);
}
h1 {
    text-align: center;
    color: #ff4b6e;
}
.stButton>button {
    background-color: #ff4b6e;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background: white;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

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

# ---------------- VOICE ENGINE ----------------
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... Speak now")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except:
        return "Sorry, I couldn't understand"

# ---------------- FUNCTIONS ----------------
def detect_face_shape(filename):
    name = filename.lower()
    if "round" in name:
        return "round"
    elif "oval" in name:
        return "oval"
    elif "square" in name:
        return "square"
    else:
        return "oval"

def get_style(face, occasion):
    if occasion == "Wedding":
        hair = "Elegant bun, braided updo 💍"
        outfit = "Red, maroon, gold, royal blue 👗"
    elif occasion == "Party":
        hair = "Loose curls, ponytail 🎉"
        outfit = "Black, glitter, bold colors ✨"
    elif occasion == "College":
        hair = "Simple ponytail or braid 🎓"
        outfit = "Casual denim, pastel shades 💙"
    elif occasion == "Festival":
        hair = "Braids with flowers 🌸"
        outfit = "Bright ethnic colors 🌈"
    else:
        hair = "Natural hairstyle 🌿"
        outfit = "Neutral colors 🤍"
    return hair, outfit

def detect_emotion(text):
    text = text.lower()
    if any(w in text for w in ["sad","low","tired"]):
        return "sad"
    elif any(w in text for w in ["happy","excited"]):
        return "happy"
    elif any(w in text for w in ["stress","worried"]):
        return "stressed"
    else:
        return "neutral"

def chatbot(msg):
    emotion = detect_emotion(msg)

    if emotion == "sad":
        return "It's okay 💖 Take rest and relax 🌸"
    elif emotion == "happy":
        return "Love your vibe! Keep shining ✨"
    elif emotion == "stressed":
        return "Take a break 🧘 Drink water 💧"
    else:
        if "skin" in msg.lower():
            return "Cleanse, moisturize & sunscreen 🌞"
        return "I'm here for your glow up ✨"

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- TITLE ----------------
st.markdown("<h1>✨ Beauty Plus Glow-Up Planner</h1>", unsafe_allow_html=True)
st.write("Upgrade your style, track progress & feel amazing 💖")

# ---------------- LOGIN / REGISTER ----------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        st.success("✅ Account created!")

    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "Login":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            st.session_state.user = user
            st.success("🎉 Logged in!")
        else:
            st.error("❌ Invalid credentials")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MAIN APP ----------------
if st.session_state.user:
    st.sidebar.success(f"Welcome {st.session_state.user[1]}")
    page = st.sidebar.selectbox("Options", ["Dashboard", "Style", "Chatbot"])

    # -------- Dashboard --------
    if page == "Dashboard":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📸 Upload Your Glow-Up Progress")

        col1, col2, col3 = st.columns(3)

        with col1:
            before = st.file_uploader("Before Image")
            if before:
                st.image(before)

        with col2:
            after = st.file_uploader("After Image")
            if after:
                st.image(after)

        with col3:
            face = st.file_uploader("Face Image")

        if st.button("Save Progress"):
            if before and after and face:
                os.makedirs("uploads", exist_ok=True)

                with open(os.path.join("uploads", before.name), "wb") as f:
                    f.write(before.getbuffer())
                with open(os.path.join("uploads", after.name), "wb") as f:
                    f.write(after.getbuffer())

                face_shape = detect_face_shape(face.name)

                c.execute("INSERT INTO progress (user_id, before_img, after_img) VALUES (?,?,?)",
                          (st.session_state.user[0], before.name, after.name))
                conn.commit()

                st.success(f"✨ Saved! Face shape: {face_shape}")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------- Style --------
    elif page == "Style":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👗 Style Recommendation")

        face = st.selectbox("Face Shape", ["oval","round","square"])
        occasion = st.selectbox("Occasion", ["Wedding","Party","College","Festival"])

        if st.button("✨ Get Style"):
            hair, outfit = get_style(face, occasion)
            st.write("💇 Hair:", hair)
            st.write("👗 Outfit:", outfit)

        st.markdown('</div>', unsafe_allow_html=True)

    # -------- Chatbot --------
    elif page == "Chatbot":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💬 Voice Assistant")

        col1, col2 = st.columns(2)

        # TEXT
        with col1:
            msg = st.text_input("Type your message")
            if st.button("Send"):
                reply = chatbot(msg)
                st.write("👤", msg)
                st.write("🤖", reply)
                speak(reply)

        # VOICE
        with col2:
            if st.button("🎙 Speak"):
                voice = listen()
                st.write("👤", voice)
                reply = chatbot(voice)
                st.write("🤖", reply)
                speak(reply)

        st.markdown('</div>', unsafe_allow_html=True)