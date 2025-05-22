import streamlit as st
from PIL import Image
import json
import paho.mqtt.client as mqtt
import random

# --- CONFIGURACIÓN MQTT ---
BROKER = "broker.mqttdashboard.com"
PORT = 1883
CLIENT_ID = "CONTROL-VOZ-MQTT"

client = mqtt.Client(CLIENT_ID)

def on_publish(client, userdata, mid):
    st.info(f"Mensaje publicado con id: {mid}")

st.title("Reconocimiento facial simulado (solo imagen)")

# Subida de imagen
imagen_subida = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if imagen_subida:
    imagen_pil = Image.open(imagen_subida).convert("RGB")
    st.image(imagen_pil, caption="Imagen subida", use_column_width=True)

    # Simulación de "detección de rostro"
    st.markdown("🔍 Simulando análisis de imagen...")

    # Aquí podrías usar heurísticas (como tamaño de imagen o colores predominantes)
    # Para este ejemplo, usaremos una simulación aleatoria (80% probabilidad de detectar humano)
    detectado = random.choices(["humano", "no humano"], weights=[0.8, 0.2], k=1)[0]

    if detectado == "humano":
        st.success("✅ ¡Rostro humano detectado!")

        # Enviar mensaje MQTT
        result = {"codigo": "casa"}
        msg = json.dumps(result)

        client.on_publish = on_publish
        client.connect(BROKER, PORT)
        client.publish("nicolas_ctrl", msg)

        st.info("📡 Comando enviado vía MQTT")
    else:
        st.warning("❌ No se detectó un rostro humano.")
