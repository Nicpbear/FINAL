import streamlit as st
from streamlit_webrtc import webrtc_streamer
import speech_recognition as sr
import threading
import queue
import paho.mqtt.client as mqtt
import re

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

st.title("🎤 Desbloqueo por voz con streamlit-webrtc")

texto_reconocido = st.empty()
mensaje = st.empty()

# Cola para pasar audio desde el callback a la función principal
q = queue.Queue()

def audio_callback(frame):
    audio_bytes = frame.to_ndarray(format="int16")
    q.put(audio_bytes)
    return frame

def reconocer_voz():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        if not q.empty():
            audio_data = q.get()
            audio = sr.AudioData(audio_data.tobytes(), 16000, 2)

            try:
                texto = recognizer.recognize_google(audio, language="es-ES")
                st.session_state['voz'] = texto.lower()
                break
            except sr.UnknownValueError:
                st.session_state['voz'] = ""
                break
            except Exception as e:
                st.session_state['voz'] = ""
                break

webrtc_streamer(
    key="mic",
    audio_frame_callback=audio_callback,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

if 'voz' not in st.session_state:
    st.session_state['voz'] = ""

if st.button("Reconocer palabra"):
    reconocer_voz()
    voz = st.session_state['voz']

    if voz:
        texto_reconocido.write(f"🔊 Dijiste: **{voz}**")
        voz_limpia = re.sub(r'[^\w\s]', '', voz).strip().lower()
        if voz_limpia == "casa":
            mensaje.markdown("<h2 style='color:green;'>🚪 Puerta desbloqueada</h2>", unsafe_allow_html=True)
            enviar_mensaje_mqtt("unlock")
        else:
            mensaje.markdown("<h2 style='color:red;'>❌ Palabra incorrecta</h2>", unsafe_allow_html=True)
    else:
        mensaje.markdown("<h2 style='color:orange;'>❌ No se reconoció la voz, intenta de nuevo</h2>", unsafe_allow_html=True)
