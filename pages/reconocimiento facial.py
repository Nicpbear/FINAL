import cv2
import streamlit as st
import openai
import paho.mqtt.client as mqtt

# 🔐 Clave API de OpenAI desde Secrets en Streamlit Cloud
openai.api_key = st.secrets["openai_api_key"]

# 🟩 Configuración MQTT
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
MQTT_TOPIC = "IMIA"

client = mqtt.Client()

def connect_mqtt():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        st.success("✅ Conectado a MQTT")
    except Exception as e:
        st.error(f"❌ Error conectando a MQTT: {e}")

connect_mqtt()

st.title("🔍 Reconocimiento Facial + MQTT")

# 🔵 Cargar clasificador Haar para rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# 🟠 Inicializar la cámara
cap = cv2.VideoCapture(0)

frame_window = st.image([])

face_detected_flag = False

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            st.warning("⚠️ No se pudo capturar la imagen.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 🟢 Si se detecta un rostro humano, enviar mensaje MQTT una sola vez
        if len(faces) > 0 and not face_detected_flag:
            st.success("👤 Humano detectado: Enviando mensaje MQTT...")
            client.publish(MQTT_TOPIC, "casa")
            face_detected_flag = True

        frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
except Exception as e:
    st.error(f"❌ Error: {e}")
finally:
    cap.release()
    client.loop_stop()
    client.disconnect()
