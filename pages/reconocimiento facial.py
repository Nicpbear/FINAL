import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import openai


def encode_image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")

st.set_page_config(page_title="Detección de Persona en Imagen", layout="centered")

st.title("📸 Captura una foto y detecta si hay una persona")

api_key = st.text_input("Ingresa tu OpenAI API Key", type="password")
if not api_key:
    st.warning("Por favor ingresa tu API key para continuar.")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key
client = OpenAI(api_key=api_key)

captured_image = st.camera_input("Toma una foto")

if captured_image:
    img = Image.open(captured_image)
    st.image(img, caption="Imagen capturada", use_container_width=True)

    with st.spinner("Analizando imagen..."):
        try:
            base64_img = encode_image_to_base64(img)

            prompt_text = "En español, dime si en esta imagen hay una persona o humano y descríbela brevemente."

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            }
                        },
                    ],
                }
            ]

            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=500, stream=True
            ):
                delta_content = completion.choices[0].delta.get("content")
                if delta_content:
                    full_response += delta_content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error al analizar la imagen: {e}")

else:
    st.write("Por favor, toma una foto para analizar.")
