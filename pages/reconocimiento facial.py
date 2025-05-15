import os
import streamlit as st
import base64
import openai

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Analisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen:🤖🏞️")

ke = st.text_input('Ingresa tu Clave')
if ke:
    openai.api_key = ke

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Image", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

show_details = st.checkbox("Adiciona detalles sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area("Adiciona contexto de la imagen aqui:")

analyze_button = st.button("Analiza la imagen")

if uploaded_file and ke and analyze_button:
    with st.spinner("Analizando ..."):
        base64_image = encode_image(uploaded_file)

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
                    },
                ],
            }
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200
            )
            answer = response['choices'][0]['message']['content']
            st.markdown(answer)
        except Exception as e:
            st.error(f"Error al llamar a OpenAI: {e}")
else:
    if analyze_button:
        if not uploaded_file:
            st.warning("Por favor sube una imagen.")
        if not ke:
            st.warning("Por favor ingresa tu API key.")

