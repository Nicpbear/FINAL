import streamlit as st
import paho.mqtt.client as mqtt
import tempfile
import os

# Configuración del broker MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

# Función para enviar mensaje MQTT
def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

st.title("🔊 Desbloqueo por voz")
st.write("Di la palabra secreta para desbloquear.")

audio_bytes = st.audio_recorder("🎤 Graba tu voz", format="audio/wav")

if audio_bytes:
    # Guardar el archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    # Usar speech_recognition solo localmente (asumiendo que ya funciona en tu entorno)
    import speech_recognition as sr
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

    # Limpiar archivo temporal
    os.remove(temp_audio_path)


