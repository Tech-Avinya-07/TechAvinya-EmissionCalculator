from typing import Optional

class LineItem:
    def __init__(self):
        self.line_item_id: int = 0
        self.invoice_id: Optional[int] = None
        self.item_name: str = ""
        self.item_qty: Optional[float] = None
        self.item_amount: Optional[float] = None
