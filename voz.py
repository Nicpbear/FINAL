import streamlit as st
import paho.mqtt.client as mqtt
import streamlit.components.v1 as components
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

st.title("🎤 Desbloqueo por voz con vista previa de texto")
st.write("Haz clic en el botón y di la palabra secreta: **Casa**")

if "voz_detectada" not in st.session_state:
    st.session_state["voz_detectada"] = ""
    st.session_state["mensaje"] = ""

components.html("""
<html>
  <body>
    <input type="text" id="textoVoz" style="width: 100%; font-size: 1.2rem;" placeholder="Aquí aparecerá el texto reconocido" readonly />
    <button onclick="reconocer()" style="padding: 10px 20px; font-size: 16px; margin-top: 10px;">🎙️ Hablar</button>

    <script>
      function reconocer() {
          var recognition = new webkitSpeechRecognition();
          recognition.lang = "es-ES";

          recognition.onresult = function(event) {
              var texto = event.results[0][0].transcript.toLowerCase();
              document.getElementById("textoVoz").value = texto;

              // Enviar texto reconocido a Streamlit vía URL (query param)
              const iframe = document.createElement('iframe');
              iframe.style.display = 'none';
              iframe.src = '/?voz_detectada=' + encodeURIComponent(texto);
              document.body.appendChild(iframe);
          }
          recognition.start();
      }
    </script>
  </body>
</html>
""", height=150)

params = st.query_params
if "voz_detectada" in params:
    palabra = params["voz_detectada"][0]
    st.session_state["voz_detectada"] = palabra
    st.experimental_rerun()

voz = st.session_state["voz_detectada"]

# Mostrar el texto que salió en el cuadro (puedes mantenerlo visible)
st.write(f"🔊 Dijiste: **{voz}**")

# Limpiamos puntuación (como puntos, comas, etc)
voz_limpia = re.sub(r'[^\w\s]', '', voz).strip().lower()

if voz_limpia:
    if voz_limpia == "casa":
        st.markdown("<h1 style='color:green;'>🚪 Puerta desbloqueada</h1>", unsafe_allow_html=True)
        enviar_mensaje_mqtt("unlock")
    else:
        st.markdown("<h1 style='color:red;'>❌ Palabra incorrecta</h1>", unsafe_allow_html=True)

    # Limpiar para que pueda repetir después
    st.session_state["voz_detectada"] = ""

