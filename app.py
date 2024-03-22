import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import json
import tempfile
import cv2
import tabula

def extract_text_from_image(image_path):
    """
    Extract text from an image using OCR (Optical Character Recognition).

    Parameters:
        image_path (str): Path to the input image file.

    Returns:
        str: Extracted text from the image.
    """
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    return text

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF using OCR (Optical Character Recognition).

    Parameters:
        pdf_path (str): Path to the input PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

def extract_tables_from_pdf(pdf_path):
    """
    Extract tables from a PDF file.

    Parameters:
        pdf_path (str): Path to the input PDF file.

    Returns:
        list: A list of DataFrames representing the extracted tables.
    """
    tables = tabula.read_pdf(pdf_path, pages='all')
    return tables

def convert_to_dataframe(tables):
    """
    Convert extracted tables to DataFrame format.

    Parameters:
        tables (list): A list of tables extracted from the PDF.

    Returns:
        list: A list of DataFrames representing the extracted tables.
    """
    dfs = []
    for table in tables:
        df = pd.DataFrame(table)
        dfs.append(df)
    return dfs

def convert_to_json(dfs):
    """
    Convert DataFrames to JSON format.

    Parameters:
        dfs (list): A list of DataFrames.

    Returns:
        list: A list of JSON strings representing the DataFrames.
    """
    json_data = []
    for df in dfs:
        json_data.append(df.to_json())
    return json_data

# Streamlit app title
st.title("Tabular Data Extractor")

# Radio button to select file type (PDF or Image)
file_type = st.radio("Select File Type", ("PDF", "Image"))

# File uploader
uploaded_file = st.file_uploader("Upload your PDF or Image file", type=["pdf", "png", "jpg"])

# Main logic to process uploaded file
if uploaded_file is not None:
    # Save uploaded file to a temporary location
    temp_file_path = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path.close()
    with open(temp_file_path.name, "wb") as f:
        f.write(uploaded_file.getvalue())

    # Extract text and tables based on file type
    if file_type == "PDF":
        text = extract_text_from_pdf(temp_file_path.name)
        tables = extract_tables_from_pdf(temp_file_path.name)
    else:
        text = extract_text_from_image(temp_file_path.name)
        tables = []

    # Display extracted text
    st.header("Extracted Text")
    st.text(text)

    # If tables are found, display them as DataFrames and JSON data
    if tables:
        st.header("Extracted Tables")
        for i, table in enumerate(tables):
            st.write(f"Table {i+1}")
            st.write(pd.DataFrame(table))

        # Convert tables to JSON format and display
        df_json = convert_to_json(convert_to_dataframe(tables))
        for i, data in enumerate(df_json):
            st.write(f"JSON Data for Table {i+1}")
            st.json(data)

        # Download JSON files for each table
        for i, data in enumerate(df_json):
            st.markdown(f"Download JSON data for Table {i+1}")
            st.download_button(label="Download JSON", data=data, file_name=f"table_{i+1}.json", mime="application/json")

    else:
        st.warning("No tables found in the document.")
