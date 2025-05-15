import streamlit as st
import speech_recognition as sr
import paho.mqtt.client as mqtt

# Configuración MQTT (ajusta el broker y tópico según tu caso)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "tu/topico"

# Crear cliente MQTT y conectar
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

st.title("Reconocimiento de voz para abrir puerta")

r = sr.Recognizer()

# Pedir al usuario que hable
st.write("Por favor, di la palabra clave para desbloquear la puerta:")

try:
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=5)  # escuchar la voz, timeout ajustable

    # Reconocer texto usando Google
    text = r.recognize_google(audio, language="es-ES")
    st.write(f"Dijiste: {text}")

    # Validar palabra clave
    if text.lower() in ["casa", "casa."]:
        st.success("Puerta desbloqueada")
        # Enviar mensaje por MQTT
        client.publish(MQTT_TOPIC, "casa")
    else:
        st.error("Incorrecto")

except sr.WaitTimeoutError:
    st.error("No detecté ninguna voz. Intenta de nuevo.")
except sr.UnknownValueError:
    st.error("No entendí lo que dijiste. Intenta de nuevo.")
except Exception as e:
    st.error(f"Error inesperado: {e}")
