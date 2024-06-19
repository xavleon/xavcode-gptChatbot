import streamlit as st
import openai
import PyPDF2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )

        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        st.error("RateLimitError: You have exceeded your API quota. Please check your OpenAI plan and billing details.")
        return None
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
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
    
# Set page configuration including the favicon
st.set_page_config(
    page_title="Javier's GPT Chat Bot",
    page_icon="./robot.png",  # Replace with your favicon URL
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }
    .stTextInput > div > input {
        background-color: #e6eaf0;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;
        color: #333;
        
        
    }
    .stTextArea > div > textarea {
        background-color: #e6eaf0;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;
        color: #333;
        
       
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stAlert {
        background-color: #ffdede;
        color: #333;
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧠 GeniusBot: AI-Powered Assistance with PDF Insight")
st.write("Made by Xavcode")
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
    st.session_state['messages'] = [("assistant", "Hello, I am a GeniusBot: AI-Powered Assistance with PDF Insight. Developed by Javier Leon using gpt-3.5-turbo and Dall-e 3. How can I help you?")]

# Display chat messages from history on the app
for role, message in st.session_state['messages']:
    if role == 'user':
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)

# Get user input
prompt = st.chat_input("Say something")
if prompt:
    # Check if the prompt is for image generation
    if 'image of' in prompt.lower() or 'picture of' in prompt.lower():
        # Show spinner while generating the image
        with st.spinner("Generating image..."):
            image_url = generate_image(prompt)
            if image_url:
                st.image(image_url, caption="Generated Image")
                st.write(f"[Open Image in a separate window]({image_url})")
                # Store the image prompt in session state
                st.session_state['messages'].append(("user", prompt))
                st.session_state['messages'].append(("assistant", f"Here is the image based on your prompt: {prompt}"))
            else:
                st.write("Failed to generate image.")
    else:
        # Immediately display the user's message
        st.chat_message("user").write(prompt)
        st.session_state['messages'].append(("user", prompt))

        # Placeholder for assistant's response
        with st.spinner("Assistant is typing..."):
            response = generate_response(prompt)
        
        if response and not response.lower().startswith("i'm sorry, but i'm unable to directly generate images."):
            # Append the assistant's response to the session state
            st.session_state['messages'].append(("assistant", response))
            # Display the assistant's response
            st.chat_message("assistant").write(response)