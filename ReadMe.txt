Overview
This project provides a set of Python tools to process various types of datasets, particularly focused on extracting and processing text from PDFs and images. The folder includes an environment setup, necessary dependencies, and Python scripts for handling PDF and image-based data, OCR processing, and structured text extraction.

Folder Contents:
Environment Setup: The folder contains a virtual environment (env) with all the dependencies pre-installed. You can activate the environment directly.
Python Scripts:
pdf_processing.py: Handles PDF data extraction.
image_preprocessing.py: Enhances images for better OCR results.
img_text_processing.py: Processes and improves text on images before OCR.
ocr_processing.py: Extracts text from images and PDFs using OCR.
text_cleaning.py: Cleans and formats extracted text.
text_processing.py: Parses and organizes cleaned text into structured models.
Database:
ocr_results.db: SQLite database for storing structured data extracted from the processed text.
Initial Models:
A folder containing the initial models definition used for text processing and structuring the extracted data.


Installation and Setup:
Step 1: Clone the repository
----git clone <repository_url>

Step 2: Activate the Virtual Environment
Activate the pre-configured virtual environment from the folder.
----.\env\Scripts\activate

Step 4: Run the main.py Script
----python main.py
