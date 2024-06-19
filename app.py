import streamlit as st
import openai
import PyPDF2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_response(prompt):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def generate_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# Set page configuration including the favicon
st.set_page_config(
    page_title="Javier's GPT Bot",
    page_icon="https://example.com/path/to/favicon.ico",  # Replace with your favicon URL
)

st.title("🧠 Genius Bot")
st.write("Ask me anything!")
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    reader = PyPDF2.PdfFileReader(uploaded_file)
    pdf_text = ""
    for page_num in range(reader.numPages):
        page = reader.getPage(page_num)
        pdf_text += page.extract_text()
    st.text_area("Extracted PDF Text:", value=pdf_text, height=300)

# Initialize session state if not already done
if 'messages' not in st.session_state:
    st.session_state['messages'] = [("assistant", "Hello, welcome to Javier's GPT Bot!")]

# Display chat messages from history on the app
for role, message in st.session_state['messages']:
    if role == 'user':
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)

# Get user input for chat
prompt = st.chat_input("Say something")
if prompt:
    # Check if the prompt is for image generation
    if 'image of' in prompt.lower() or 'picture of' in prompt.lower():
        # Show spinner while generating the image
        with st.spinner("Generating image..."):
            image_url = generate_image(prompt)
            if image_url:
                # Display the image
                st.image(image_url, caption="Generated Image")
                # Provide a message with a clickable link to open the image in a new window
                st.session_state['messages'].append(("user", prompt))
                st.session_state['messages'].append(("assistant", f"Here is the image based on your prompt: [Open Image in New Window]({image_url})"))
            else:
                st.error("Failed to generate image.")
    else:
        # Immediately display the user's message
        st.session_state['messages'].append(("user", prompt))

        # Placeholder for assistant's response
        with st.spinner("Assistant is typing..."):
            response = generate_response(prompt)
        
        if response:
            # Append the assistant's response to the session state
            st.session_state['messages'].append(("assistant", response))

    # Display chat messages from history on the app
    for role, message in st.session_state['messages']:
        if role == 'user':
            st.chat_message("user").write(message)
        else:
            st.chat_message("assistant").write(message)
