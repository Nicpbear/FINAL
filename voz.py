import streamlit as st
import paho.mqtt.client as mqtt
import streamlit.components.v1 as components

# Configuración MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "voz/puerta"

def enviar_mensaje_mqtt(mensaje):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.publish(MQTT_TOPIC, mensaje)
    client.disconnect()

# Mostrar título e instrucciones
st.title("🎤 Desbloqueo por voz")
st.write("Haz clic en el botón y di la palabra secreta: **Casa**")

# Inicializar session_state
if "voz_detectada" not in st.session_state:
    st.session_state["voz_detectada"] = ""

# Código JS para reconocimiento y envío al frontend
components.html("""
<html>
  <body>
    <script>
      const streamlitChannel = window.parent;
      function reconocer() {
          var recognition = new webkitSpeechRecognition();
          recognition.lang = "es-ES";
          recognition.onresult = function(event) {
              var resultado = event.results[0][0].transcript.toLowerCase();
              console.log("Reconocido: " + resultado);
              const iframe = document.createElement('iframe');
              iframe.style.display = 'none';
              iframe.src = '/?voz_detectada=' + encodeURIComponent(resultado);
              document.body.appendChild(iframe);
          };
          recognition.start();
      }
    </script>
    <button onclick="reconocer()" style="padding: 10px 20px; font-size: 16px;">🎙️ Hablar</button>
  </body>
</html>
""", height=150)

# Leer palabra desde URL (query_params)
params = st.query_params
if "voz_detectada" in params:
    palabra = params["voz_detectada"]
    st.session_state["voz_detectada"] = palabra
    st.experimental_rerun()  # recarga la app para procesar el valor

# Procesar palabra
voz = st.session_state["voz_detectada"]

if voz:
    st.write(f"🔊 Dijiste: {voz}")
    if voz.strip().lower() == "casa":
        st.success("✅ Casa desbloqueada")
        enviar_mensaje_mqtt("unlock")
        st.success("🚪 Señal enviada a Wokwi vía MQTT")
        st.session_state["voz_detectada"] = ""  # limpiar para evitar repetición
    else:
        st.error("❌ Palabra incorrecta. Intenta de nuevo.")
        st.session_state["voz_detectada"] = ""
