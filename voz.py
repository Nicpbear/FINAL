import streamlit as st
import speech_recognition as sr
import paho.mqtt.client as mqtt

# MQTT config
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

# Función para publicar mensaje MQTT
def enviar_mensaje(mensaje):
    cliente = mqtt.Client()
    cliente.connect(MQTT_BROKER, MQTT_PORT, 60)
    cliente.publish(MQTT_TOPIC, mensaje)
    cliente.disconnect()

st.title("🔊 Desbloqueo por voz (MQTT + Wokwi)")

if st.button("Escuchar código de voz"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Escuchando... di la palabra clave")
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language="es-ES")
        st.write(f"🔊 Dijiste: {texto}")

        if texto.strip().lower() == "casa":
            st.success("✅ Casa desbloqueada")
            enviar_mensaje("unlock")
            st.success("🚪 Señal enviada a Wokwi vía MQTT")
        else:
            st.error("❌ Código incorrecto")

    except sr.UnknownValueError:
        st.error("❗ No se entendió el audio.")
    except sr.RequestError as e:
        st.error(f"⚠️ Error con el reconocimiento de voz: {e}")

