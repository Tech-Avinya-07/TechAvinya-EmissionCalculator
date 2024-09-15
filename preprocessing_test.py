import os
import logging
from pdf_processing import PDFProcessing
from image_preprocessing import ImagePreProcessing
from img_text_cleaning import TextCleanerScript  # Ensure this import matches your structure

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PreprocessingPipeline:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        """
        Runs the preprocessing stages: PDF to image conversion, image enhancement, and text cleaning.
        """
        logging.info("Starting the Preprocessing Pipeline...")

        # Step 1: Process PDFs and convert to images
        logging.info("Processing PDFs...")
        pdf_processor = PDFProcessing()
        pdf_processor.convert_pdf(self.input_dir)  # Only pass input_dir as output is handled internally

        # Verify that images were saved correctly
        image_files = [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith(('.jpg', '.png'))]
        if not image_files:
            logging.error("No images found in the output directory after PDF processing. Stopping pipeline.")
            return

        logging.info(f"Found {len(image_files)} images for further preprocessing.")

        # Step 2: Enhance each image using the same filename
        logging.info("Enhancing images...")
        for image_file in image_files:
            try:
                ImagePreProcessing.enhance_image_quality(image_file)  # Enhance in place
                logging.info(f"Enhanced image saved as: {image_file}")  # Assuming it overwrites the original
            except Exception as e:
                logging.error(f"Error enhancing image {image_file}: {e}")
                continue

        # Step 3: Clean text in images, using the same filename
        logging.info("Cleaning text in images...")
        text_cleaner = TextCleanerScript()  # Initialize the text cleaner
        for image_file in image_files:
            try:
                text_cleaner.execute(image_file)  # Only pass the image_file
                logging.info(f"Cleaned image saved as: {image_file}")  # Assuming it overwrites the original
            except Exception as e:
                logging.error(f"Error cleaning text in image {image_file}: {e}")
                continue

        logging.info("Preprocessing pipeline completed successfully!")

if __name__ == "__main__":
    # Define input and output directories
    input_dir = r"C:\ocr\immg"  # Update this path
    output_dir = r"C:\OCR\EnhancedImage"  # Update this path

    # Initialize and run the preprocessing pipeline
    pipeline = PreprocessingPipeline(input_dir, output_dir)
    pipeline.run()



