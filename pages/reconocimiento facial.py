import os
import streamlit as st
import base64
from openai import OpenAI

# Función para codificar la imagen a base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Análisis de imagen con cámara", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen: 🤖🏞️")

# Entrada de API key
ke = st.text_input('Ingresa tu Clave de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Inicializar cliente OpenAI
client = OpenAI(api_key=api_key)

# Captura de imagen desde la cámara
captured_image = st.camera_input("Toma una foto")

if captured_image:
    with st.expander("Imagen capturada", expanded=True):
        st.image(captured_image, use_container_width=True)

# Opción para detalles adicionales
show_details = st.toggle("Agregar detalles sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area("Agrega contexto adicional sobre la imagen:")

# Botón para analizar
analyze_button = st.button("Analizar imagen")

if captured_image is not None and api_key and analyze_button:
    with st.spinner("Analizando..."):
        base64_image = encode_image(captured_image)
        prompt_text = "Describe lo que ves en la imagen en español."
        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional:\n{additional_details}"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages, max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

elif analyze_button:
    if not captured_image:
        st.warning("Por favor, toma una foto primero.")
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
