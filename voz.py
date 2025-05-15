import streamlit as st
import paho.mqtt.client as mqtt
import streamlit.components.v1 as components

# Configuración del broker MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

# Función para enviar mensaje por MQTT
def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

st.title("🎤 Desbloqueo por voz")
st.write("Haz clic en el botón y di la palabra secreta: **Casa**")

# Componente HTML y JS incrustado que usa reconocimiento de voz
components.html("""
    <script>
    const streamlitDoc = window.parent.document;
    function enviarTexto(texto) {
        const input = streamlitDoc.querySelector('iframe[srcdoc]')?.contentWindow?.streamlitReceiveMessage;
        if (input) {
            window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: texto }, "*");
        }
    }

    function reconocerVoz() {
        var recognition = new webkitSpeechRecognition();
        recognition.lang = "es-ES";
        recognition.onresult = function(event) {
            var texto = event.results[0][0].transcript.toLowerCase();
            enviarTexto(texto);
        };
        recognition.start();
    }
    </script>

    <button onclick="reconocerVoz()" style="padding: 10px 20px; font-size: 16px;">🎙️ Hablar</button>
""", height=100)

# Recibir valor enviado por el componente JS
valor = st.query_params.get("voz")  # ya reemplazamos experimental_get_query_params

# Capturar el valor desde el iframe postMessage
valor_js = st._legacy_get_widget("component_value")  # método de fallback

if valor_js:
    st.write(f"🔊 Dijiste: {valor_js}")

    if valor_js.strip().lower() == "casa":
        st.success("✅ Casa desbloqueada")
        enviar_mensaje_mqtt("unlock")
        st.success("🚪 Señal enviada a Wokwi vía MQTT")
    else:
        st.error("❌ Palabra incorrecta. Intenta de nuevo.")
