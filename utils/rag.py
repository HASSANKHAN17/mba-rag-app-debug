import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image
from dotenv import load_dotenv
import io
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")  # Use working model

# ... rest of the code



# import google.generativeai as genai
# from PyPDF2 import PdfReader
# from PIL import Image
# import io

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# model = genai.GenerativeModel("gemini-1.5-pro")  # Use latest working model

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    return model.generate_content(["Extract and summarize useful text from this image:", image]).text

def query_documents(query, files=[]):
    context = ""
    for file in files:
        if file.type == "application/pdf":
            context += extract_text_from_pdf(file)
        elif "image" in file.type:
            context += extract_text_from_image(file)
        else:
            context += "\n[Unsupported file type]"

    prompt = f"""You are a helpful assistant for MBA Analytics students.
Use the following context to answer the query.
Context: {context}
Query: {query}
Answer:"""

    response = model.generate_content(prompt)
    return response.text
