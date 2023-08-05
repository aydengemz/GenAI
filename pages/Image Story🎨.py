# import .env
from dotenv import load_dotenv, find_dotenv
from transformers import pipeline
from langchain import PromptTemplate, LLMChain, OpenAI
import requests
import os
import streamlit as st
from PIL import Image
from auth import check_password
import openai


# img2text
def img2text(url):
    image_to_text = pipeline(
        "image-to-text", model="Salesforce/blip-image-captioning-base"
    )
    text = image_to_text(url)[0]["generated_text"]
    print(text)
    return text


def img2textFile(file):
    image_to_text = pipeline(
        "image-to-text", model="Salesforce/blip-image-captioning-base"
    )
    text = image_to_text(file)[0]["generated_text"]
    print(text)
    return text


# llm
def generate_story(scenario):
    template = """
        You are a story teller;
        You can generate a short story based on a simple narrative, the story should be no more than 20 words;

        CONTEXT: {scenario}
        STORY:
    """
    prompt = PromptTemplate(template=template, input_variables=["scenario"])

    story_llm = LLMChain(
        llm=OpenAI(model_name="gpt-3.5-turbo", temperature=1),
        prompt=prompt,
        verbose=True,
    )
    story = story_llm.predict(scenario=scenario)
    print(story)
    return story


# text to Speech
def text2speech(message, hkey):
    API_URL = (
        "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    )

    headers = {"Authorization": f"Bearer {hkey}"}

    payloads = {"inputs": message}
    response = requests.post(API_URL, headers=headers, json=payloads)
    with open("audio.flac", "wb") as file:
        file.write(response.content)


def text2speech2(message, hkey):
    API_URL = (
        "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    )

    headers = {"Authorization": f"Bearer {hkey}"}

    payloads = {"inputs": message}
    response = requests.post(API_URL, headers=headers, json=payloads)
    with open("audio2.flac", "wb") as file:
        file.write(response.content)


def text2img(message):
    API_URL = (
        "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    )
    headers = {"Authorization": "Bearer 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"}

    payloads = {"inputs": message}

    response = requests.post(API_URL, headers=headers, json=payloads)
    with open("image.jpg", "wb") as file:
        file.write(response.content)


def main():
    st.header("Image Story 📷 !")
    st.write("Generate a short story based on a word!")

    st.image("diagrams/imagestory.png", use_column_width=True)

    openAIKey = st.text_input("Enter your OpenAI API Key")
    huggingKey = st.text_input("Enter your HuggingFace API Key")

    st.text("")
    st.text("")

    input = st.text_input("Image Url", "")

    if st.button("Generate Story"):
        openai.api_key = openAIKey
        txt = img2text(input)
        st.write(txt)
        story = generate_story(txt)
        st.write(story)

        text2speech(story, huggingKey)
        st.audio("audio.flac")

    input2 = st.text_input("Topic Text", "")

    if st.button("Enter Text"):
        openai.api_key = openAIKey
        text2img(input2)

        with st.expander("See Image"):
            image = Image.open("image.jpg")
            st.image(image, caption="Your Image")

        text = img2textFile(image)
        with st.expander("See Text"):
            st.write(text)

        story = generate_story(text)
        with st.expander("See Story"):
            st.write(story)

        text2speech2(story, huggingKey)
        st.write("Listen to Story")
        st.audio("audio2.flac")

        st.video("https://www.youtube.com/watch?v=_j7JEDWuqLE")


if __name__ == "__main__":
    main()
