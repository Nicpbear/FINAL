import streamlit as st
import speech_recognition as sr
import paho.mqtt.client as mqtt

# Configuración MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

st.title("Reconocimiento de voz: solo 'casa'")

if st.button("Grabar y reconocer"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Escuchando... Di la palabra 'casa'")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language="es-ES")
        st.write(f"Dijiste: **{texto}**")

        # Compara texto ignorando punto final y mayúsculas
        texto_normalizado = texto.lower().strip()
        if texto_normalizado == "casa" or texto_normalizado == "casa.":
            st.success("🚪 Puerta desbloqueada")
            enviar_mensaje_mqtt("unlock")
        else:
            st.error("❌ Palabra incorrecta")

    except sr.UnknownValueError:
        st.error("No se entendió lo que dijiste")
    except sr.RequestError as e:
        st.error(f"Error con el servicio de reconocimiento: {e}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")

