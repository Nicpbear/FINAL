import streamlit as st
import paho.mqtt.client as mqtt
import tempfile
import os
import speech_recognition as sr

# Configuración del broker MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

st.title("🔊 Desbloqueo por voz")
st.write("Sube una grabación de voz diciendo la palabra clave.")

# Subir archivo de audio
audio_file = st.file_uploader("🎤 Sube un archivo de audio (WAV)", type=["wav"])

if audio_file is not None:
    # Mostrar reproductor de audio
    st.audio(audio_file, format='audio/wav')

    # Guardar archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_file.read())
        temp_audio_path = temp_audio.name

    # Procesar el audio
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_audio_path) as source:
        audio = recognizer.record(source)

    try:
        texto = recognizer.recognize_google(audio, language="es-ES")
        st.write(f"🔊 Dijiste: {texto}")

        if texto.strip().lower() == "casa":
            st.success("✅ Casa desbloqueada")
            enviar_mensaje_mqtt("unlock")
            st.success("🚪 Señal enviada a Wokwi vía MQTT")
        else:
            st.error("❌ Código incorrecto. Intenta de nuevo.")

    except sr.UnknownValueError:
        st.error("❗ No se entendió el audio.")
    except sr.RequestError as e:
        st.error(f"⚠️ Error con el reconocimiento de voz: {e}")

    # Borrar archivo temporal
    os.remove(temp_audio_path)

