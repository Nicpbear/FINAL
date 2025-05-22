import streamlit as st
import numpy as np
import face_recognition
from PIL import Image
import json
import paho.mqtt.client as mqtt
import os

# --- CONFIGURACIÓN MQTT ---
BROKER = "broker.mqttdashboard.com"
PORT = 1883
CLIENT_ID = "CONTROL-VOZ-MQTT"

client = mqtt.Client(CLIENT_ID)

def on_publish(client, userdata, mid):
    st.info(f"Mensaje publicado con id: {mid}")

st.title("Reconocimiento facial desde imagen (sin OpenCV)")

imagen_subida = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if imagen_subida:
    imagen_pil = Image.open(imagen_subida).convert("RGB")
    imagen_np = np.array(imagen_pil)

    rostros = face_recognition.face_locations(imagen_np)

    for (top, right, bottom, left) in rostros:
        imagen_np[top:bottom, left:left] = [0, 255, 0]  # Colorea el rostro

    st.image(imagen_np, caption="Resultado", use_column_width=True)

    if len(rostros) > 0:
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
