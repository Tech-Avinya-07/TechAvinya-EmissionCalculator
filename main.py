import os
import logging
from pdf_processing import PDFProcessing
from image_preprocessing import ImagePreProcessing
from img_text_cleaning import TextCleanerScript  
from ocr_processing import PerformingOCR
from receipt_processing import process_receipt
from database import Database
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OCRPipeline:
    def __init__(self, input_dir, output_dir, db_path="ocr_results.db"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.db = Database(db_path)  # Initialize Database

    def run(self):
        """
        Main method to run the full OCR pipeline.
        """
        logging.info("Starting the OCR pipeline...")

        # Step 1: Process PDFs and images
        logging.info("Processing files in the input directory...")
        PDFProcessing.convert_files(self.input_dir)

        # Verify that images were saved correctly
        image_files = [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith('_thresholded.jpg')]
        if not image_files:
            logging.error("No thresholded images found in the output directory after processing.")
            return  # Stop the pipeline if no images are found
        
        logging.info(f"Found {len(image_files)} images for OCR processing.")

        # Step 2: Preprocess each image
        logging.info("Preprocessing images...")
        for image_file in image_files:
            try:
                processed_image_path = ImagePreProcessing.enhance_image_quality(image_file)
                logging.info(f"Image enhancement completed for: {processed_image_path}")
            except Exception as e:
                logging.error(f"Error during image enhancement for {image_file}: {e}")
                continue

        # Step 3: Clean the text inside the images
        logging.info("Cleaning text inside images...")
        text_cleaner = TextCleanerScript()
        for image_file in image_files:
            cleaned_image = text_cleaner.execute(image_file)  # Clean the text in the image
            if cleaned_image:
                logging.info(f"Image text cleaned: {image_file}")

        # Step 4: Perform OCR on each cleaned image
        logging.info("Performing OCR...")
        ocr_processor = PerformingOCR()
        ocr_results = []
        for image_file in image_files:
            text_rows = ocr_processor.do_ocr(image_file)  # Perform OCR
            if text_rows:
                extracted_text = " ".join([row.word for row in text_rows])  # Join the words together
                logging.info(f"OCR completed for: {image_file}")
                print(f"Extracted text from {image_file}: {extracted_text}")

                # Step 5: Process the extracted text to calculate carbon footprint
                receipt_id = int(time.time())  # Use UNIX timestamp as receipt_id
                logging.info(f"Processing receipt for file {image_file} with receipt ID: {receipt_id}")
                receipt_result = process_receipt(extracted_text, receipt_id)

                # Step 6: Store the results in the database
                if receipt_result:
                    for item in receipt_result:
                        item_name = item['item_name']
                        carbon_footprint = item['carbon_footprint']
                        category = item['category']

                        self.db.insert_receipt_data(receipt_id, item_name, carbon_footprint, category)
                        logging.info(f"Stored in database: {item_name}, {carbon_footprint} kg CO2e, Category: {category}")

                ocr_results.append((image_file, extracted_text))

        logging.info("OCR pipeline completed.")

if __name__ == "__main__":
    # Define input and output directories
    input_dir = r"C:\Users\shaha\OneDrive\Desktop\samples"
    output_dir = r"C:\OCR\EnhancedImage"

    # Initialize and run the OCR pipeline
    pipeline = OCRPipeline(input_dir, output_dir)
    pipeline.run()

