import os
import logging
from pdf_processing import PDFProcessing
from image_preprocessing import ImagePreProcessing
from img_text_cleaning import TextCleanerScript  
from ocr_processing import PerformingOCR
from Text_cleaning import Identify  
from text_processing import PopInvoice
from database import Database

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

        # Step 1: Process PDFs and convert to images
        logging.info("Processing PDFs...")
        pdf_processor = PDFProcessing()
        pdf_processor.convert_pdf(self.input_dir)

        # Verify that images were saved correctly
        image_files = [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith('_thresholded.jpg')]
        if not image_files:
            logging.error("No thresholded images found in the output directory after PDF processing.")
            return  # Stop the pipeline if no images are found
        
        logging.info(f"Found {len(image_files)} images for OCR processing.")

        # Step 2: Preprocess each image
        logging.info("Preprocessing images...")
        for image_file in image_files:
            try:
                ImagePreProcessing.enhance_image_quality(image_file)
                logging.info(f"Image enhancement completed for: {image_file}")
            except Exception as e:
                logging.error(f"Error during image enhancement for {image_file}: {e}")
                continue

        # Step 3: Clean the text inside the images
        logging.info("Cleaning text inside images...")
        text_cleaner = TextCleanerScript()  # Initialize the text cleaner
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
                ocr_results.append((image_file, text_rows))
                logging.info(f"OCR completed for: {image_file}")

        # Step 5: Clean the OCR results
        logging.info("Cleaning OCR results...")
        invoice_list = []
        for image_file, text_rows in ocr_results:
            cleaned_text_rows = Identify.remove_space(text_rows)  # Clean the OCR text
            invoice = PopInvoice.populate_invoice(cleaned_text_rows, image_file)  # Process structured data
            invoice_list.append(invoice)
            logging.info(f"Invoice populated from: {image_file}")

        # Step 6: Save the structured data into the database
        logging.info("Saving results in the database...")
        for invoice in invoice_list:
            self.db.insert_invoice(invoice)  # Save each invoice into the database
        logging.info("All results saved in the database.")

        logging.info("OCR pipeline completed successfully!")

if __name__ == "__main__":
    # Define input and output directories
    input_dir = r"C:\Users\shaha\OneDrive\Desktop\ocr model (1)\dataset\img_files_f"
    output_dir = r"C:\OCR\EnhancedImage"

    # Initialize and run the OCR pipeline
    pipeline = OCRPipeline(input_dir, output_dir)
    pipeline.run()
