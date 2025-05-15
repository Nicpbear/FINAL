import streamlit as st
import speech_recognition as sr
import paho.mqtt.client as mqtt
import re

# Configuración MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

st.title("Reconocimiento de voz para desbloquear")

# Botón para iniciar reconocimiento
if st.button("Grabar y reconocer"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Escuchando... Di la palabra clave")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=5)
    
    try:
        texto = r.recognize_google(audio, language="es-ES")
        texto_limpio = re.sub(r'[^\w\s]', '', texto).strip().lower()
        st.write(f"Dijiste: **{texto}**")

        if texto_limpio == "casa":
            st.success("🚪 Puerta desbloqueada")
            enviar_mensaje_mqtt("unlock")
        else:
            st.error("❌ Palabra incorrecta")

    except sr.UnknownValueError:
        st.error("No se pudo entender la palabra, intenta de nuevo.")
    except sr.RequestError as e:
        st.error(f"Error al conectarse al servicio de reconocimiento: {e}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")

