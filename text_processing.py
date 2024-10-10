from ocr_models.Invoice import Invoice
from ocr_models.LineItem import LineItem
from ocr_models.Row import Row
from Text_cleaning import DataType
import re
from typing import List, Optional

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
            if row.type == DataType.DATETIME and invoice.invoice_date is None:
                invoice.invoice_date = row.word
            elif row.type == DataType.STRING and invoice.vendor_name == "":
                invoice.vendor_name = PopInvoice.extract_vendor_name(page_items, i)

        return invoice

    @staticmethod
    def extract_amount(page_items: List[Row], start_index: int) -> Optional[str]:
        """Extracts the total amount from a list of rows."""
        for row in page_items[start_index:]:
            if row.type == DataType.DOUBLE:
                return row.word
        return None

    @staticmethod
    def extract_line_items(page_items: List[Row], start_index: int) -> List[LineItem]:
        """Extracts line items from the page."""
        line_items = []
        current_item = LineItem()
        current_line = None

        for i in reversed(range(start_index)):
            row = page_items[i]
            if current_line is None or row.line != current_line:
                if current_item.item_name:
                    line_items.append(current_item)
                    current_item = LineItem()
                current_line = row.line

            PopInvoice.update_line_item(row, current_item)

        if current_item.item_name:
            line_items.append(current_item)

        return line_items

    @staticmethod
    def update_line_item(row: Row, current_item: LineItem) -> None:
        """Updates the current line item based on the row type."""
        if row.type in {DataType.INT32, DataType.INT64}:
            current_item.item_qty = PopInvoice.parse_quantity(row.word)
        elif row.type == DataType.DOUBLE:
            current_item.item_amount = PopInvoice.parse_amount(row.word)
        else:
            current_item.item_name = row.word + " " + current_item.item_name

    @staticmethod
    def parse_quantity(quantity_str: str) -> float:
        """Parses the quantity string and returns a float."""
        try:
            return float(quantity_str)
        except ValueError:
            return 0.0  # Handle as needed

    @staticmethod
    def parse_amount(amount_str: str) -> str:
        """Parses the amount string and returns a formatted amount."""
        cleaned_amount = re.sub(r'[^\d.]', '', amount_str)
        try:
            amount = float(cleaned_amount)
            return f"${amount:.2f}"
        except ValueError:
            return "$0.00"  # Handle as needed

    @staticmethod
    def extract_vendor_name(page_items: List[Row], start_index: int) -> str:
        """Extracts the vendor name from the OCR text."""
        vendor_name = []
        current_line = page_items[start_index].line

        for row in page_items[start_index:]:
            if row.line != current_line:
                break
            if row.type == DataType.STRING and row.word:
                vendor_name.append(row.word)

        return " ".join(vendor_name).strip()