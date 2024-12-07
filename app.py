from dotenv import load_dotenv
import os
import io
import base64
import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genai
import subprocess

# Load environment variables
load_dotenv()

# Configure the generative AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get a response from Gemini AI
def get_gemini_response(input_text, pdf_content, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_text, pdf_content[0], prompt])
        return response.text
    except Exception as e:
        raise Exception(f"Error in AI response generation: {e}")

# Function to check if Poppler is installed and accessible
def check_poppler():
    try:
        # Check Poppler installation
        poppler_path = subprocess.run(["which", "pdfinfo"], capture_output=True, text=True)
        if poppler_path.returncode == 0:
            st.write(f"Poppler found at: {poppler_path.stdout.strip()}")
        else:
            st.error("Poppler is not installed or not in PATH.")
    except Exception as e:
        st.error(f"Error checking Poppler installation: {e}")

# Function to process the uploaded PDF
def input_pdf_setup(uploaded_file):
    try:
        if uploaded_file is not None:
            # Check if Poppler is installed
            check_poppler()

            # Convert the PDF to images using the correct Poppler path
            poppler_path = r'C:\poppler\Library\bin'  # Path for Poppler in the cloud environment
            images = pdf2image.convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)

            # Process the first page
            first_page = images[0]

            # Convert the first page to bytes
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Prepare PDF content in base64
            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()  # Encode to base64
                }
            ]
            return pdf_parts
        else:
            raise FileNotFoundError("No file uploaded.")
    except Exception as e:
        raise Exception(f"Error in processing PDF file: {e}")

# Streamlit UI setup
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input for job description
input_text = st.text_area("Job Description:", key="input")

# File uploader for resume
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

# Check if the file is uploaded
if uploaded_file is not None:
    st.write("PDF uploaded successfully.")

# Buttons for actions
submit1 = st.button("Tell me about your resume")
submit3 = st.button("Percentage match")

# Prompts for generative AI
input_prompt1 = """
You are an experienced Technical HR with tech experience in the field of Data Science, Full Stack Web development, Big Data Engineering, DEVOPS, and Data Analysis. 
Your task is to review the provided resume against the job description for these profiles. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of Data Science, Full Stack Web development, Big Data Engineering, DEVOPS, and Data Analysis. 
Your task is to evaluate the resume against the provided job description. 
Give me the percentage of match if the resume matches the job description. 
First, the output should come as a percentage, then keywords missing, and last, final thoughts.
"""

# Handling button clicks
if submit1:
    if uploaded_file is not None:
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_text, pdf_content, input_prompt1)
            st.subheader("The response is:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred while processing your resume: {e}")
    else:
        st.error("Please upload the resume before submitting.")

if submit3:
    if uploaded_file is not None:
        try:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_text, pdf_content, input_prompt3)
            st.subheader("The response is:")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred while processing your resume: {e}")
    else:
        st.error("Please upload the resume before submitting.")
