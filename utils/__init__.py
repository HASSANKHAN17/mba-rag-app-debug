import os
import io
import pandas as pd
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PIL import Image
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_image(file):
    image = Image.open(file)
    return model.generate_content(["Extract and summarize useful text from this image:", image]).text

def extract_text_from_csv(file):
    df = pd.read_csv(file)
    return df.to_string()

def extract_text_from_excel(file):
    df = pd.read_excel(file)
    return df.to_string()

def query_documents(query, files=[]):
    context = ""
    for file in files:
        file_type = file.type
        try:
            if file_type == "application/pdf":
                context += extract_text_from_pdf(file) + "\n\n"
            elif "image" in file_type:
                context += extract_text_from_image(file) + "\n\n"
            elif file_type == "text/csv":
                context += extract_text_from_csv(file) + "\n\n"
            elif file_type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]:
                context += extract_text_from_excel(file) + "\n\n"
            else:
                context += f"\n[Unsupported file type: {file.name}]"
        except Exception as e:
            context += f"\n[Error reading {file.name}: {e}]"

    prompt = f"""You are a helpful assistant for MBA Analytics students.
Use the following context to answer the query.
Context: {context}
Query: {query}
Answer:"""

    response = model.generate_content(prompt)
    return response.text
