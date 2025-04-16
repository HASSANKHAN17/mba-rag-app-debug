import os
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PIL import Image
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_image(file):
    image = Image.open(file)
    return model.generate_content(["Extract and summarize useful text from this image:", image]).text

def extract_text_from_file(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(file)
    elif "image" in file.type:
        return extract_text_from_image(file)
    elif file.name.endswith((".csv", ".xls", ".xlsx")):
        return ""  # analytics handler will use pandas
    return "[Unsupported file type]"

def query_documents(query, files=[]):
    context = ""
    for file in files:
        context += extract_text_from_file(file)
    prompt = f"""You are a helpful assistant for MBA Analytics students.
Use the following context to answer the query.
Context: {context}
Query: {query}
Answer:"""
    response = model.generate_content(prompt)
    return response.text

# 🧠 Recognize analytic commands
def is_analysis_query(query):
    keywords = ["eda", "regression", "cluster", "visualize", "plot", "scatter", "summary", "describe"]
    return any(k in query.lower() for k in keywords)

# 🎯 Run analytics if a data file is present
def analyze_file(query, files):
    data_file = next((f for f in files if f.name.endswith((".csv", ".xls", ".xlsx"))), None)
    if not data_file or not is_analysis_query(query):
        return None

    # Load data
    try:
        if data_file.name.endswith(".csv"):
            df = pd.read_csv(data_file)
        else:
            df = pd.read_excel(data_file)
    except Exception as e:
        return {"summary": f"❌ Failed to read file: {e}"}

    summary_text = ""
    visuals = []

    # Summary stats
    if "eda" in query.lower() or "summary" in query.lower() or "describe" in query.lower():
        summary_text += "### 🔍 Summary Statistics\n"
        summary_text += df.describe().to_markdown()

    # Correlation heatmap
    # Correlation heatmap
    if "correlation" in query.lower() or "eda" in query.lower():
        numeric_df = df.select_dtypes(include="number")
        if not numeric_df.empty:
            plt.figure(figsize=(10, 6))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
            plt.title("Correlation Heatmap")
            visuals.append(plt.gcf())


    # Histogram
    if "distribution" in query.lower() or "hist" in query.lower() or "eda" in query.lower():
        numeric_cols = df.select_dtypes(include="number").columns[:1]
        if len(numeric_cols):
            col = numeric_cols[0]
            plt.figure()
            sns.histplot(df[col], kde=True)
            plt.title(f"Histogram of {col}")
            visuals.append(plt.gcf())

    # Scatter plot
    if "scatter" in query.lower() and len(df.select_dtypes(include="number").columns) >= 2:
        cols = df.select_dtypes(include="number").columns[:2]
        plt.figure()
        sns.scatterplot(x=df[cols[0]], y=df[cols[1]])
        plt.title(f"Scatter Plot: {cols[0]} vs {cols[1]}")
        visuals.append(plt.gcf())

    return {
        "summary": summary_text,
        "visuals": visuals
    }
