import streamlit as st
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from PIL import Image
import json
import os

# --- CONFIGURACIÓN MQTT ---
BROKER = "broker.mqttdashboard.com"
PORT = 1883
CLIENT_ID = "CONTROL-VOZ-MQTT"

client = mqtt.Client(CLIENT_ID)

# Callback para cuando se publique un mensaje
def on_publish(client, userdata, mid):
    st.info(f"Mensaje publicado con id: {mid}")

# Modelo de detección de rostros OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

st.title("Reconocimiento facial desde imagen")

# Subir imagen
imagen_subida = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if imagen_subida is not None:
    imagen_pil = Image.open(imagen_subida).convert("RGB")
    imagen_np = np.array(imagen_pil)
    imagen_gris = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2GRAY)

    rostros = face_cascade.detectMultiScale(imagen_gris, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in rostros:
        cv2.rectangle(imagen_np, (x, y), (x + w, y + h), (0, 255, 0), 2)

    st.image(imagen_np, caption="Resultado", use_column_width=True)

    # Aquí simulamos el resultado del reconocimiento; si hay rostros, asumimos comando "casa"
    if len(rostros) > 0:
        # Simulamos un "result" para integrar tu lógica
        result = {"GET_TEXT": "casa"}

        if result and "GET_TEXT" in result:
            command = result.get("GET_TEXT").strip().lower()

            st.markdown('<p class="section-title">📋 Comando Reconocido:</p>', unsafe_allow_html=True)
            st.code(command, language='markdown')

            client.on_publish = on_publish
            client.connect(BROKER, PORT)

            if command in ["casa", "casa."]:
                st.success("✅ Puerta desbloqueada")
                msg = json.dumps({"codigo": "casa"})
            else:
                st.error("❌ Incorrecto")
                msg = json.dumps({"codigo": "incorrecto"})

            client.publish("nicolas_ctrl", msg)

            os.makedirs("temp", exist_ok=True)
    else:
        st.warning("No se detectaron rostros en la imagen.")
