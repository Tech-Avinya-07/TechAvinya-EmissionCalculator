from ocr_models.Invoice import Invoice
from ocr_models.LineItem import LineItem
import sqlite3
from typing import List

class Database:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        """Creates the invoices and line_items tables."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id TEXT PRIMARY KEY,
                    vendor_name TEXT,
                    invoice_date TEXT,
                    total_amount REAL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS line_items (
                    invoice_id TEXT,
                    item_name TEXT,
                    item_qty REAL,
                    item_amount REAL,
                    FOREIGN KEY(invoice_id) REFERENCES invoices(id)
                )
            """)

    def insert_invoice(self, invoice):
        """Inserts an invoice and its line items into the database."""
        with self.conn:
            self.conn.execute("""
                INSERT INTO invoices (id, vendor_name, invoice_date, total_amount)
                VALUES (?, ?, ?, ?)
            """, (invoice.invoice_id, invoice.vendor_name, invoice.invoice_date, invoice.total_amount))

            for item in invoice.line_items:
                self.conn.execute("""
                    INSERT INTO line_items (invoice_id, item_name, item_qty, item_amount)
                    VALUES (?, ?, ?, ?)
                """, (invoice.invoice_id, item.item_name, item.item_qty, item.item_amount))

   


