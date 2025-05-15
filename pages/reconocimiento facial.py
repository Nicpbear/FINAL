import streamlit as st
import base64
from openai import OpenAI

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

st.title("Análisis de Imagen con cámara")

api_key = st.text_input('Ingresa tu Clave OpenAI', type="password")
client = None
if api_key:
    client = OpenAI(api_key=api_key)

captured_image = st.camera_input("Toma una foto")

if captured_image:
    # Mostrar la imagen
    st.image(captured_image, use_container_width=True)

    if client and st.button("Analiza la imagen"):
        with st.spinner("Analizando..."):
            base64_image = encode_image(captured_image)
            prompt_text = "Describe lo que ves en la imagen en español"

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
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
                st.error(f"Error: {e}")
