import streamlit as st
import cv2
import paho.mqtt.client as mqtt
import os
import openai
from PIL import Image
import numpy as np

# Configura la clave de OpenAI usando variable de entorno (como en tu código de voz)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Configuración MQTT
broker = "broker.mqttdashboard.com"
puerto = 1883
topico = "IMIA"

cliente_mqtt = mqtt.Client()

# Conexión al broker MQTT
def conectar_mqtt():
    try:
        cliente_mqtt.connect(broker, puerto, 60)
        cliente_mqtt.loop_start()
        st.success("✅ Conectado al broker MQTT")
    except Exception as e:
        st.error(f"❌ Error al conectar MQTT: {e}")

# Publica mensaje "casa"
def enviar_mensaje_acceso():
    cliente_mqtt.publish(topico, "casa")
    st.success("📨 Mensaje MQTT enviado: 'casa'")

# Título
st.title("🔍 Reconocimiento Facial con MQTT")

# Botón para iniciar
start = st.button("Iniciar cámara y detectar rostro")

if start:
    conectar_mqtt()

    # Carga del modelo Haar Cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("❌ No se pudo acceder a la cámara")
    else:
        st.info("🎥 Cámara encendida. Buscando rostros...")

        placeholder = st.empty()

        rostro_detectado = False
        while not rostro_detectado:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                rostro_detectado = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            placeholder.image(frame_rgb, channels="RGB", caption="Detectando...")

            if rostro_detectado:
                enviar_mensaje_acceso()
                st.success("✅ Rostro detectado")
                break

        cap.release()
        placeholder.empty()
