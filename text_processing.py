from ocr_models.Invoice import Invoice
from ocr_models.LineItem import LineItem
from ocr_models.Row import Row
from Text_cleaning import DataType
import re
from typing import List

class LineItem:
    def __init__(self):
        self.item_qty = 0
        self.item_amount = 0.0
        self.item_name = ""

class Invoice:
    def __init__(self):
        self.invoice_id = ""
        self.invoice_date = None
        self.vendor_name = ""
        self.total_amount = None
        self.line_items = []

class Row:
    def __init__(self, line, column, word, type):
        self.line = line
        self.column = column
        self.word = word
        self.type = type

class PopInvoice:
    @staticmethod
    def populate_invoice(page_items: List[Row], file_name: str) -> Invoice:
        """Populates an Invoice object with details extracted from OCR rows."""
        invoice = Invoice()
        invoice.invoice_id = file_name
        
        # Look for the total amount
        for i in reversed(range(len(page_items))):
            if page_items[i].word and page_items[i].word.lower() in {"total", "payment"}:
                invoice.total_amount = PopInvoice.extract_amount(page_items, i)
                invoice.line_items = PopInvoice.extract_line_items(page_items, i)
                break

        # Extract invoice date and vendor name
        for i, row in enumerate(page_items):
            if row.type == DataType.DATETIME:
                invoice.invoice_date = row.word
            if row.type == DataType.STRING and invoice.vendor_name == "":
                invoice.vendor_name = PopInvoice.extract_vendor_name(page_items, i)

        return invoice

    @staticmethod
    def extract_amount(page_items: List[Row], start_index: int) -> str:
        """Extracts the total amount from a list of rows."""
        for row in page_items[start_index:]:
            if row.type == DataType.DOUBLE:
                return row.word
        return None



    @staticmethod
    def extract_line_items(page_items: List[Row], start_index: int) -> List[LineItem]:
        """Extracts line items from the page."""
        line_items = []
        current_line = None
        current_item = LineItem()

        for i in reversed(range(start_index)):
            row = page_items[i]
            if current_line is None or row.line != current_line:
                if current_item.item_name:
                    line_items.append(current_item)
                    current_item = LineItem()
                current_line = row.line

            if row.type in {DataType.INT32, DataType.INT64}:
                try:
                    current_item.item_qty = float(row.word)
                except ValueError:
                    current_item.item_qty = 0  # or handle the error as needed
            elif row.type == DataType.DOUBLE:
                # Remove any non-numeric characters except for the decimal point
                cleaned_amount = re.sub(r'[^\d.]', '', row.word)
                try:
                    current_item.item_amount = float(cleaned_amount)
                    # Add the dollar sign back
                    current_item.item_amount = f"${current_item.item_amount:.2f}"
                except ValueError:
                    current_item.item_amount = "$0.00"  # or handle the error as needed
            else:
                current_item.item_name = row.word + " " + current_item.item_name

        if current_item.item_name:
            line_items.append(current_item)

        return line_items



    @staticmethod
    def extract_vendor_name(page_items: List[Row], start_index: int) -> str:
        """Extracts the vendor name from the OCR text."""
        vendor_name = ""
        current_line = page_items[start_index].line

        for row in page_items[start_index:]:
            if row.line != current_line:
                break
            if row.type == DataType.STRING and row.word:
                vendor_name += f" {row.word}"

        return vendor_name.strip()
