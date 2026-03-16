import xmlrpc.client
import os
import time
import json
import logging
from datetime import datetime, date

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FinanceWatcher")

# Configuration
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")
CHECK_INTERVAL = 600  # Check every 10 minutes

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'AI_Employee_Vault'))
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, 'Needs_Action')
PROCESSED_FILE = os.path.join(os.path.dirname(__file__), '.processed_invoices.json')

class FinanceWatcher:
    def __init__(self):
        self.url = ODOO_URL if not ODOO_URL.endswith("/") else ODOO_URL[:-1]
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = None
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        self.processed_ids = self.load_processed()

    def load_processed(self):
        if os.path.exists(PROCESSED_FILE):
            try:
                with open(PROCESSED_FILE, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def save_processed(self):
        with open(PROCESSED_FILE, 'w') as f:
            json.dump(list(self.processed_ids), f)

    def authenticate(self):
        try:
            self.uid = self.common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
            if self.uid:
                logger.info(f"Authenticated successfully as User ID: {self.uid}")
                return True
            else:
                logger.error("Authentication failed.")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def check_overdue_invoices(self):
        if not self.uid:
            if not self.authenticate(): return

        today = date.today().isoformat()
        domain = [
            ['move_type', '=', 'out_invoice'],
            ['state', '=', 'posted'],
            ['payment_state', 'in', ['not_paid', 'partial']],
            ['invoice_date_due', '<', today]
        ]
        
        try:
            ids = self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, 'account.move', 'search', [domain])
            if not ids: return

            new_ids = [i for i in ids if i not in self.processed_ids]
            if not new_ids: return

            fields = ['name', 'partner_id', 'amount_total', 'invoice_date_due']
            records = self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, 'account.move', 'read', [new_ids], {'fields': fields})

            for record in records:
                self.create_alert(record)
                self.processed_ids.add(record['id'])
            
            self.save_processed()

        except Exception as e:
            logger.error(f"Error checking invoices: {e}")

    def create_alert(self, invoice):
        logger.info(f"Creating alert for overdue invoice {invoice['name']}")
        if not os.path.exists(NEEDS_ACTION_DIR):
            logger.error(f"Vault directory not found: {NEEDS_ACTION_DIR}")
            return

        filename = f"FINANCE_OVERDUE_{invoice['name'].replace('/', '_')}.md"
        filepath = os.path.join(NEEDS_ACTION_DIR, filename)
        
        content = f"""---
type: finance_alert
subtype: overdue_invoice
priority: high
status: pending
created: {datetime.now().isoformat()}
---

## Overdue Invoice Alert
**Invoice:** {invoice['name']}
**Customer:** {invoice['partner_id'][1] if invoice['partner_id'] else 'Unknown'}
**Amount:** {invoice['amount_total']}
**Due Date:** {invoice['invoice_date_due']}

### Suggested Actions
- [ ] Send reminder email to customer
- [ ] Check bank for payment
"""
        with open(filepath, 'w') as f:
            f.write(content)

    def run(self):
        logger.info("Starting Finance Watcher...")
        while True:
            self.check_overdue_invoices()
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    watcher = FinanceWatcher()
    watcher.run()
