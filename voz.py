import os
import time
import json
import paho.mqtt.client as paho
import streamlit as st
from PIL import Image
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# --- CONFIGURACIÓN MQTT ---
BROKER = "broker.mqttdashboard.com"
PORT = 1883
CLIENT_ID = "CONTROL-VOZ-MQTT"

message_received = ""

def on_publish(client, userdata, result):
    print("✅ Mensaje MQTT enviado.")

def on_message(client, userdata, message):
    global message_received
    message_received = str(message.payload.decode("utf-8"))
    st.success(f"📩 MQTT dice: {message_received}")

client = paho.Client(CLIENT_ID)
client.on_message = on_message

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Acceso Inteligente por Voz", layout="centered")
st.markdown("""
    <style>
    .big-title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #2E86C1;
        margin-bottom: 10px;
    }
    .section-title {
        font-size: 22px;
        margin-top: 30px;
        color: #154360;
        font-weight: bold;
    }
    .instructions {
        font-size: 16px;
        color: #424949;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🔒 Acceso Inteligente por Reconocimiento de Voz</p>', unsafe_allow_html=True)

# Imagen decorativa
st.image("voice_ctrl.jpg", width=280, caption="Sistema de Seguridad Activado")

# Expansor para instrucciones
with st.expander("ℹ️ Cómo usar el sistema de acceso"):
    st.markdown("""
    <div class="instructions">
    1. Presiona el botón <b>Iniciar Reconocimiento de Voz</b>.<br>
    2. Pronuncia la palabra clave: <code>casa</code>.<br>
    3. Si el sistema detecta la palabra clave, <b>desbloqueará la puerta</b>.<br>
    4. Si dices otra palabra, el acceso será denegado.<br>
    5. El sistema envía el resultado a través de MQTT.
    </div>
    """, unsafe_allow_html=True)

# Botón Bokeh personalizado
st.markdown('<p class="section-title">🎤 Activar Reconocimiento de Voz</p>', unsafe_allow_html=True)

stt_button = Button(label="🎙️ Iniciar Reconocimiento de Voz", width=320)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value !== "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", { detail: value }));
        }
    };
    recognition.start();
"""))

# Captura del evento
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listener",
    refresh_on_update=False,
    override_height=100,
    debounce_time=0
)

# Resultado del reconocimiento
if result and "GET_TEXT" in result:
    command = result.get("GET_TEXT").strip().lower()
    
    st.markdown('<p class="section-title">📝 Palabra detectada:</p>', unsafe_allow_html=True)
    st.code(command, language='markdown')

    client.on_publish = on_publish
    client.connect(BROKER, PORT)

    if command in ["casa", "casa."]:
        st.success("🔓 Acceso concedido: Puerta desbloqueada")
        msg = json.dumps({"codigo": "casa"})
    else:
        st.error("⛔ Acceso denegado: Código incorrecto")
        msg = json.dumps({"codigo": "incorrecto"})

    client.publish("nicolas_ctrl", msg)

    os.makedirs("temp", exist_ok=True)
