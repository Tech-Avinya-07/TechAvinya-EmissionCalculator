from ocr_models.LineItem import LineItem
from typing import List, Optional
from datetime import datetime

class Invoice:
    def __init__(self):
        self.invoice_id: str = ""
        self.vendor_name: str = ""
        self.invoice_date: Optional[datetime] = None
        self.total_amount: str = ""
        self.line_items: List['LineItem'] = []
