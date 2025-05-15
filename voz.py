import streamlit as st
import paho.mqtt.client as mqtt
import json

# Configuración del broker MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

# Función para enviar mensaje a Wokwi por MQTT
def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

# Título de la app
st.title("🔐 Reconocimiento de voz para desbloqueo")
st.write("Pulsa el botón y di la palabra secreta: **Casa**")

# HTML + JS para grabar voz con reconocimiento de Google
st.markdown("""
<script>
function iniciarReconocimiento() {
    var recognition = new webkitSpeechRecognition();
    recognition.lang = "es-ES";
    recognition.onresult = function(event) {
        var resultado = event.results[0][0].transcript.toLowerCase();
        console.log("Reconocido: " + resultado);
        const streamlitEvent = new CustomEvent("streamlit:mensaje", {
            detail: resultado
        });
        window.dispatchEvent(streamlitEvent);
    };
    recognition.start();
}
</script>

<button onclick="iniciarReconocimiento()">🎙️ Hablar</button>
""", unsafe_allow_html=True)

# Capturar resultado de JS usando streamlit_javascript si lo tienes o JSBridge personalizado
valor = st.experimental_get_query_params().get("voz", [None])[0]

# Método alternativo para recibir eventos desde JS
from streamlit_javascript import st_javascript

resultado = st_javascript("""
    new Promise((resolve) => {
        window.addEventListener("streamlit:mensaje", (e) => {
            resolve(e.detail);
        });
    });
""")

if resultado:
    st.write(f"🔊 Dijiste: {resultado}")

    if resultado.strip().lower() == "casa":
        st.success("✅ Casa desbloqueada")
        enviar_mensaje_mqtt("unlock")
        st.success("🚪 Señal enviada a Wokwi vía MQTT")
    else:
        st.error("❌ Código incorrecto. Intenta de nuevo.")

