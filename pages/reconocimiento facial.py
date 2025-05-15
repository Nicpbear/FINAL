import os
import streamlit as st
import base64
import openai
from PIL import Image  # Importar PIL para abrir imágenes

# Función para codificar la imagen en base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Configuración de la página
st.set_page_config(page_title="Análisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Análisis de Imagen: 🤖🏞️")

# Entrada para la API Key
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY', None)

# Validación de API Key
if not api_key:
    st.warning("Por favor ingresa tu API key para continuar.")
    st.stop()

# Configurar API key para openai
openai.api_key = api_key

# Subida de imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    try:
        # Intentamos abrir la imagen con PIL
        image = Image.open(uploaded_file)
        with st.expander("Imagen", expanded=True):
            st.image(image, caption=uploaded_file.name, width=700)  # Ajusta el tamaño si deseas

    except Exception as e:
        st.error(f"No se pudo mostrar la imagen. Asegúrate de que sea un archivo de imagen válido. Error: {e}")
        st.stop()

    # Botón para análisis
    analyze_button = st.button("Analiza la imagen")

    if analyze_button:
        with st.spinner("Analizando..."):
            base64_image = encode_image(uploaded_file)

            # Pregunta simple al modelo
            prompt_text = (
                "¿Hay una persona o humano en esta imagen? "
                "Responde solo 'Sí' o 'No' y justifica brevemente en español."
            )

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
                    max_tokens=150
                )
                full_response = response['choices'][0]['message']['content']
                respuesta_lower = full_response.lower()

                if "sí" in respuesta_lower or "si" in respuesta_lower:
                    st.success("✅ Reconocimiento positivo: Se detecta humano en la imagen.")
                    st.info(f"Respuesta del modelo: {full_response}")
                else:
                    st.error("❌ Verificación no exitosa: No se detecta humano en la imagen.")
                    st.info(f"Respuesta del modelo: {full_response}")

            except Exception as e:
                st.error(f"Error al analizar la imagen: {e}")
else:
    st.info("Por favor, sube una imagen para analizar.")
