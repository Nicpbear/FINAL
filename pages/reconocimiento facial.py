import os
import streamlit as st
import base64
import openai

# Función para codificar la imagen a base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Análisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen:🤖🏞️")

ke = st.text_input('Ingresa tu Clave (API Key)', type="password")
os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ['OPENAI_API_KEY']
openai.api_key = api_key

uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

show_details = st.checkbox("Añadir detalles sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area("Añade contexto de la imagen aquí:")

analyze_button = st.button("Analizar imagen")

if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando ..."):
        base64_image = encode_image(uploaded_file)
        prompt_text = "Describe lo que ves en la imagen en español."

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

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
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
            )
            full_response = response['choices'][0]['message']['content']
            st.markdown(full_response)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    if analyze_button:
        if not uploaded_file:
            st.warning("Por favor, sube una imagen.")
        if not api_key:
            st.warning("Por favor ingresa tu API Key.")
