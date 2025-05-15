import streamlit as st
import os
import base64
import openai

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

st.set_page_config(page_title="Análisis de Imagen con Cámara", layout="centered")
st.title("Análisis de Imagen: 🤖🏞️")

# Input para la API Key
api_key = st.text_input("Ingresa tu clave OpenAI (API Key):", type="password")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=api_key)
else:
    st.warning("Por favor ingresa tu API Key para continuar.")
    st.stop()

# Capturar imagen desde la cámara
captured_image = st.camera_input("Toma una foto")

if captured_image is not None:
    # Mostrar imagen capturada
    image_bytes = captured_image.getvalue()
    st.image(image_bytes, caption="Imagen capturada", use_container_width=True)

    # Botón para analizar la imagen
    if st.button("Analiza la imagen"):
        with st.spinner("Analizando..."):
            base64_image = encode_image(image_bytes)
            prompt_text = "¿Hay una persona o un humano en esta imagen? Responde en español con una explicación breve."

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
                        },
                    ],
                }
            ]

            try:
                full_response = ""
                message_placeholder = st.empty()
                for completion in client.chat.completions.create(
                    model="gpt-4o", messages=messages, max_tokens=300, stream=True
                ):
                    if completion.choices[0].delta.content is not None:
                        full_response += completion.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

            except Exception as e:
                st.error(f"Error al analizar la imagen: {e}")
else:
    st.info("Por favor, toma una foto usando la cámara.")
