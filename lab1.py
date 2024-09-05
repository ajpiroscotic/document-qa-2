import streamlit as st
from openai import OpenAI
import PyPDF2
import io

# function to validate the API Keys
real_api_key = st.secrets["api_key"]
def validate_api_key():
    if openai_api_key:
        if openai_api_key != real_api_key:
            st.error("The provided API key does not match the standard key. Please use the correct API key.")
            st.session_state["api_key_valid"] = False
        else:
            try:
                client = OpenAI(api_key=openai_api_key)
                client.models.list()
                st.success("API key is valid!")
                st.session_state["api_key_valid"] = True
            except Exception as e:
                st.error(f"Invalid API key: {e}")
                st.session_state["api_key_valid"] = False
    else:
        st.error("Please enter your OpenAI API key.")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Declare session state variables
if 'document_content' not in st.session_state:
    st.session_state.document_content = None
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False

# Show title and description
st.title("📄 Document question answering agent")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝")
else:
    validate_api_key()
    if st.session_state.get("api_key_valid", False):
        # Create an OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Let the user upload a file
        uploaded_file = st.file_uploader(
            "Upload a document (.txt or .pdf)", type=("txt", "pdf")
        )

        # Process the file when it's uploaded
        if uploaded_file and not st.session_state.file_processed:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == 'txt':
                st.session_state.document_content = uploaded_file.read().decode()
            elif file_extension == 'pdf':
                st.session_state.document_content = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
            else:
                st.error("Unsupported file type.")
                st.stop()
            st.session_state.file_processed = True

        # Document is cleared once removed for the user
        if not uploaded_file:
            st.session_state.document_content = None
            st.session_state.file_processed = False

        # Ask the user for a question
        question = st.text_area(
            "Now ask a question about the document!",
            placeholder="Can you give me a short summary?",
            disabled=not st.session_state.document_content,
        )

        if st.session_state.document_content and question:
            messages = [
                {
                    "role": "user",
                    "content": f"Here's a document: {st.session_state.document_content} \n\n---\n\n {question}",
                }
            ]

            # Generate an answer using the OpenAI API
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )

            # Stream the response to the app
            st.write_stream(stream)

