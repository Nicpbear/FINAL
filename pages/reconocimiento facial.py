import streamlit as st
import base64
import openai

st.set_page_config(page_title="Detección de personas en imagen", layout="centered")

st.title("Detección de persona en la imagen 📸")

api_key = st.text_input("Ingresa tu API Key de OpenAI", type="password")

if api_key:
    openai.api_key = api_key

    captured_image = st.camera_input("Toma una foto")

    if captured_image is not None:
        st.image(captured_image, caption="Imagen capturada", use_container_width=True)

        # Codificar imagen a base64 para enviar a OpenAI
        img_bytes = captured_image.getvalue()
        base64_img = base64.b64encode(img_bytes).decode()

        prompt = (
            "Eres un modelo que analiza imágenes y responde solo con 'Sí' o 'No'. "
            "Dime si en esta imagen hay una persona o un humano. "
            "Imagen en base64: " + base64_img
        )

        if st.button("Analizar imagen"):
            with st.spinner("Analizando..."):
                messages = [
                    {"role": "user", "content": prompt}
                ]

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=10,
                        temperature=0
                    )
                    answer = response['choices'][0]['message']['content'].strip()
                    st.success(f"Respuesta del modelo: {answer}")
                except Exception as e:
                    st.error(f"Error al llamar a OpenAI: {e}")

else:
    st.warning("Por favor ingresa tu API Key para usar la aplicación.")
