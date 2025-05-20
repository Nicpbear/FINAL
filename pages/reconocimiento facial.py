import streamlit as st
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from PIL import Image
import io

# Configuración del broker MQTT
broker = "broker.hivemq.com"
puerto = 1883
topico = "reconocimiento/facial"

# Conexión al broker MQTT
cliente = mqtt.Client()
cliente.connect(broker, puerto, 60)

# Cargar el modelo de detección de rostros de OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Título de la app
st.title("Reconocimiento facial desde imagen")

# Cargar imagen desde el usuario
imagen_subida = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if imagen_subida is not None:
    # Leer la imagen
    imagen_pil = Image.open(imagen_subida).convert("RGB")
    imagen_np = np.array(imagen_pil)

    # Convertir a escala de grises
    imagen_gris = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2GRAY)

    # Detectar rostros
    rostros = face_cascade.detectMultiScale(imagen_gris, scaleFactor=1.1, minNeighbors=5)

    # Dibujar rectángulos sobre los rostros
    for (x, y, w, h) in rostros:
        cv2.rectangle(imagen_np, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Mostrar resultados
    st.image(imagen_np, caption="Resultado", use_column_width=True)

    # Enviar mensaje MQTT si hay al menos un rostro
    if len(rostros) > 0:
        cliente.publish(topico, '{"codigo": "casa"}')
        st.success("Humano reconocido. Mensaje MQTT enviado: 'casa'")
    else:
        st.warning("No se detectaron rostros en la imagen.")
