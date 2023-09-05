# Import necessary libraries and modules
from dotenv import find_dotenv, load_dotenv
from transformers import pipeline
from langchain import PromptTemplate, LLMChain, OpenAI
import requests
import os
import streamlit as st

# Load environment variables from a .env file
load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Define the Streamlit application main function
def main():
    # Configure Streamlit app settings
    st.set_page_config(page_title="image to audio story", page_icon="📖")

    # Create a header for the app
    st.header("Turn image into audio story")

    # Allow user to upload an image file
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    # Check if an image has been uploaded
    if uploaded_file is not None:
        print(uploaded_file)

        # Read and save the uploaded image file
        bytes_data = uploaded_file.getvalue()
        with open(uploaded_file.name, "wb") as file:
            file.write(bytes_data)

        # Display the uploaded image
        st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)

        # Step 1: Convert the image to text using an image-to-text pipeline
        scenario = img2text(uploaded_file.name)

        # Step 2: Generate a short story based on the extracted text
        story = generate_story(scenario)

        # Step 3: Convert the generated story text to audio
        text2speech(story)

        # Display the extracted scenario and generated story in expandable sections
        with st.expander("Scenario"):
            st.write(scenario)
        with st.expander("Generated Story"):
            st.write(story)

        # Play the generated audio
        st.audio("audio.flac")

# Step 1: Convert an image to text using an image-to-text pipeline
def img2text(url):
    image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
    text = image_to_text(url)[0]['generated_text']
    print(text)
    return text

# Step 2: Generate a short story based on a scenario using a language model
def generate_story(scenario):
    template= """
    you are a story teller;
    you can generate a short story based on a simple narrative, the story should be no more than 20 words;

    CONTEXT: {scenario}
    STORY: 
    """

    prompt = PromptTemplate(template=template, input_variables=["scenario"])

    story_llm = LLMChain(llm=OpenAI(
        model_name="gpt-3.5-turbo", temperature=1), prompt=prompt, verbose=True)

    story = story_llm.predict(scenario=scenario)
    print(story)
    return story

# Step 3: Convert text to speech using an external API
def text2speech(message):
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}

    payloads = {
        "inputs": message
    }

    response = requests.post(API_URL, headers=headers, json=payloads)
    with open('audio.flac', 'wb') as file:
        file.write(response.content)

# Execute the main function when the script is run directly
if __name__ == '__main__':
    main()
