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
CLIENT_ID = "CONTROL-FACIAL-MQTT"

client = mqtt.Client(CLIENT_ID)

def on_publish(client, userdata, mid):
    st.info(f"📤 Mensaje publicado con ID: {mid}")

# Modelo de detección de rostros OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- INTERFAZ ---
st.set_page_config(page_title="Desbloqueo Facial", layout="centered")

st.markdown("""
    <style>
    .big-title { font-size:36px; font-weight:bold; text-align:center; color:#2196F3; }
    .section-title { font-size:24px; margin-top:30px; color:#333; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">Sistema de Desbloqueo Facial 🏠</p>', unsafe_allow_html=True)

# Imagen decorativa (debes subir esta imagen a tu repositorio de GitHub y llamar desde allí si usas la app desplegada)
st.image(
    "https://raw.githubusercontent.com/Nicpbear/FINAL/main/face_unlock.jpg",
    width=900,
    caption="Reconocimiento Facial Activado"
)




# Expansor para instrucciones
with st.expander("🔎 ¿Cómo funciona el sistema?"):
    st.markdown("""
    1. Sube una imagen que contenga un rostro.
    2. El sistema detectará automáticamente si hay un rostro presente.
    3. Si se detecta un rostro, se asumirá un comando de desbloqueo correcto ("casa").
    4. El comando será enviado vía MQTT.
    5. Si no se detectan rostros, no se enviará ningún comando.
    """)

# Título sección
st.markdown('<p class="section-title">📤 Sube tu imagen para verificar identidad</p>', unsafe_allow_html=True)

imagen_subida = st.file_uploader("Selecciona una imagen (JPG, JPEG o PNG)", type=["jpg", "jpeg", "png"])

if imagen_subida is not None:
    imagen_pil = Image.open(imagen_subida).convert("RGB")
    imagen_np = np.array(imagen_pil)
    imagen_gris = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2GRAY)

    rostros = face_cascade.detectMultiScale(imagen_gris, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in rostros:
        cv2.rectangle(imagen_np, (x, y), (x + w, y + h), (0, 255, 0), 2)

    st.image(imagen_np, caption="Resultado del Análisis", use_column_width=True)

    if len(rostros) > 0:
        result = {"GET_TEXT": "casa"}  # Simulación

        if result and "GET_TEXT" in result:
            command = result.get("GET_TEXT").strip().lower()

            st.markdown('<p class="section-title">📋 Comando Reconocido:</p>', unsafe_allow_html=True)
            st.code(command, language='markdown')

            client.on_publish = on_publish
            client.connect(BROKER, PORT)

            if command in ["casa", "casa."]:
                st.success("✅ Acceso concedido: Puerta desbloqueada")
                msg = json.dumps({"codigo": "casa"})
            else:
                st.error("❌ Código incorrecto")
                msg = json.dumps({"codigo": "incorrecto"})

            client.publish("nicolas_ctrl", msg)
            os.makedirs("temp", exist_ok=True)
    else:
        st.warning("🚫 No se detectaron rostros en la imagen. Acceso denegado.")
