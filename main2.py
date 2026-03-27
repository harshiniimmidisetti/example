import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import time

st.set_page_config(page_title="AI Skin Analyzer", layout="centered")

st.title("💄 AI Skin Analyzer")

# Create uploads folder
os.makedirs("uploads", exist_ok=True)

# ---------------- FACE DETECTION ----------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def detect_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x,y), (x+w,y+h), (255,0,0), 2)

    return image, len(faces)

# ---------------- SKIN ANALYSIS ----------------
def detect_skin_issues(image):
    results = []

    face = cv2.resize(image, (300, 300))

    # Pimples
    hsv = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 70, 50])
    upper_red = np.array([10, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    if cv2.countNonZero(mask) > 600:
        results.append("Pimples")

    # Dark circles
    h, w, _ = face.shape
    eye = face[int(h*0.5):int(h*0.75), int(w*0.2):int(w*0.8)]
    if np.mean(cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)) < 70:
        results.append("Dark Circles")

    # Skin type
    brightness = np.mean(face)
    if brightness > 170:
        skin_type = "Oily"
    elif brightness < 100:
        skin_type = "Dry"
    else:
        skin_type = "Normal"

    return results, skin_type

# ---------------- PRODUCT SUGGESTION ----------------
def recommend(issues, skin_type):
    products = []

    if "Pimples" in issues:
        products += ["Salicylic Face Wash", "Niacinamide Serum"]

    if "Dark Circles" in issues:
        products += ["Eye Cream"]

    if skin_type == "Dry":
        products += ["Moisturizer"]

    if skin_type == "Oily":
        products += ["Oil-Free Gel"]

    if not products:
        products = ["Cleanser + Sunscreen"]

    return list(set(products))

# ---------------- INPUT ----------------
st.subheader("📸 Upload or Capture Image")

uploaded = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])
camera = st.camera_input("Take Photo")

# ---------------- PROCESS ----------------
if st.button("Analyze"):

    if uploaded is None and camera is None:
        st.error("Please upload or capture image")
    
    else:
        # Choose image
        if uploaded is not None:
            img = Image.open(uploaded)
            filename = f"upload_{int(time.time())}.jpg"
        else:
            img = Image.open(camera)
            filename = f"camera_{int(time.time())}.jpg"

        # Save image
        filepath = os.path.join("uploads", filename)
        img.save(filepath)

        st.success(f"Saved in uploads/{filename}")

        # Convert to OpenCV
        img_np = np.array(img)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Face detect
        face_img, count = detect_face(img_cv)

        # Skin analysis
        issues, skin_type = detect_skin_issues(img_cv)
        products = recommend(issues, skin_type)

        # ---------------- OUTPUT ----------------
        st.image(face_img, caption=f"Faces Detected: {count}")

        st.subheader("🔍 Results")
        st.write("Skin Type:", skin_type)

        if issues:
            st.write("Issues:", issues)
        else:
            st.write("No major issues")

        st.subheader("💡 Suggested Products")
        for p in products:
            st.write("✔", p)