import base64
import openai
import streamlit as st
from PIL import Image
import paho.mqtt.client as paho
import json

# --- CONFIGURACIÓN OPENAI ---
openai.api_key = st.secrets["openai_api_key"]  # Asegúrate de configurar esto en Streamlit Secrets

# --- CONFIGURACIÓN MQTT ---
BROKER = "broker.mqttdashboard.com"
PORT = 1883
CLIENT_ID = "FACIAL-MQTT"

def on_publish(client, userdata, result):
    print("✅ Mensaje MQTT enviado.")

mqtt_client = paho.Client(CLIENT_ID)
mqtt_client.on_publish = on_publish
mqtt_client.connect(BROKER, PORT)

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Reconocimiento Facial", layout="centered")
st.title("📸 Desbloqueo de Puerta con Reconocimiento Facial")

uploaded_image = st.file_uploader("Sube una imagen para verificar acceso:", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="Imagen subida", use_column_width=True)

    # Codifica la imagen en base64
    buffered = open(uploaded_image.name, "rb")
    image_bytes = buffered.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Envía a GPT-4o con visión
    prompt = "¿Puedes confirmar si hay una figura humana en esta imagen? Responde solo sí o no."

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres un detector de personas experto."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]}
        ],
        temperature=0.2
    )

    respuesta = response["choices"][0]["message"]["content"]
    respuesta_lower = respuesta.strip().lower()

    st.markdown("### 🤖 Respuesta del modelo:")
    st.info(respuesta)

    # Lógica de decisión y MQTT
    if "sí" in respuesta_lower or "si" in respuesta_lower:
        st.success("✅ Puerta desbloqueada (humano detectado)")
        msg = json.dumps({"codigo": "casa"})
    else:
        st.error("❌ Incorrecto (no se detectó humano)")
        msg = json.dumps({"codigo": "incorrecto"})

    mqtt_client.publish("nicolas_ctrl", msg)
