import streamlit as st
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

st.title("🎤 Desbloqueo por voz con vista previa de texto")
st.write("Haz clic en el botón y di la palabra secreta: **Casa**")

# Código HTML y JS para reconocimiento de voz
html_code = """
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

              // Actualizar query params para que Streamlit detecte la palabra
              window.history.replaceState(null, null, '?voz_detectada=' + encodeURIComponent(texto));
          }
          recognition.start();
      }
    </script>
  </body>
</html>
"""

st.components.v1.html(html_code, height=150)

params = st.query_params
voz = params.get("voz_detectada", [""])[0]

if voz:
    st.write(f"🔊 Dijiste: **{voz}**")

    voz_limpia = re.sub(r'[^\w\s]', '', voz).strip().lower()

    if voz_limpia == "casa":
        st.markdown("<h1 style='color:green;'>🚪 Puerta desbloqueada</h1>", unsafe_allow_html=True)
        enviar_mensaje_mqtt("unlock")
    else:
        st.markdown("<h1 style='color:red;'>❌ Palabra incorrecta</h1>", unsafe_allow_html=True)

    if st.button("🔄 Intentar de nuevo"):
        # Limpiar query params para reiniciar
        st.experimental_set_query_params()
        st.experimental_rerun()
