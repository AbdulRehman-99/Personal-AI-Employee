import xmlrpc.client
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OdooMCP")

# Load configuration from environment variables
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

class OdooClient:
    def __init__(self):
        self.url = Odoo_URL if not Odoo_URL.endswith("/") else Odoo_URL[:-1]
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = self.authenticate()
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

    def authenticate(self):
        try:
            uid = self.common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
            if uid:
                logger.info(f"Authenticated successfully as User ID: {uid}")
                return uid
            else:
                logger.error("Authentication failed.")
                return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    def execute_kw(self, model, method, *args, **kwargs):
        if not self.uid:
            return {"error": "Not authenticated"}
        try:
            return self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, model, method, args, kwargs)
        except Exception as e:
            return {"error": str(e)}

    def create_invoice(self, partner_name, lines):
        # 1. Find partner ID
        partner_ids = self.execute_kw('res.partner', 'search', [[['name', '=', partner_name]]])
        if isinstance(partner_ids, dict) and "error" in partner_ids: return partner_ids
        
        if not partner_ids:
            # Create partner if not exists
            partner_id = self.execute_kw('res.partner', 'create', [{'name': partner_name}])
        else:
            partner_id = partner_ids[0]

        # 2. Prepare invoice lines
        invoice_lines = []
        for line in lines:
            # line expected: {"product": "Service", "quantity": 1, "price": 100}
            invoice_lines.append((0, 0, {
                'name': line.get('product', 'Service'),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price', 0.0),
            }))

        # 3. Create invoice
        invoice_id = self.execute_kw('account.move', 'create', [{
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_line_ids': invoice_lines,
        }])
        
        if isinstance(invoice_id, int):
            # Optional: Post the invoice
            # self.execute_kw('account.move', 'action_post', [[invoice_id]])
            return {"status": "success", "invoice_id": invoice_id, "message": f"Invoice created for {partner_name}"}
        else:
            return {"status": "error", "message": str(invoice_id)}

    def list_invoices(self, state='posted', limit=10):
        domain = [['move_type', '=', 'out_invoice']]
        if state:
            domain.append(['state', '=', state])
        
        ids = self.execute_kw('account.move', 'search', domain, {'limit': limit})
        if not ids: return []
        
        fields = ['name', 'partner_id', 'amount_total', 'invoice_date', 'state', 'payment_state']
        records = self.execute_kw('account.move', 'read', [ids], {'fields': fields})
        return records

    def get_financial_summary(self):
        # Determine current month start/end if needed, for now just total posted
        domain_in = [['move_type', '=', 'out_invoice'], ['state', '=', 'posted']] # Revenue
        domain_out = [['move_type', '=', 'in_invoice'], ['state', '=', 'posted']] # Expenses

        # This is a simplification. Real accounting would query account.move.line for specific accounts.
        # But for "Freelancer/Small Business" simple invoice tracking is often enough.
        
        invoices = self.execute_kw('account.move', 'search_read', [domain_in], {'fields': ['amount_total']})
        bills = self.execute_kw('account.move', 'search_read', [domain_out], {'fields': ['amount_total']})
        
        total_revenue = sum(inv['amount_total'] for inv in invoices) if isinstance(invoices, list) else 0
        total_expenses = sum(bill['amount_total'] for bill in bills) if isinstance(bills, list) else 0
        
        return {
            "revenue": total_revenue,
            "expenses": total_expenses,
            "net_income": total_revenue - total_expenses
        }

client = OdooClient()

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "odoo-mcp-server", "version": "1.0.0"}
                    }
                }
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "create_invoice",
                                "description": "Create a customer invoice in Odoo",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "partner_name": {"type": "string"},
                                        "lines": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "product": {"type": "string"},
                                                    "quantity": {"type": "number"},
                                                    "price": {"type": "number"}
                                                }
                                            }
                                        }
                                    },
                                    "required": ["partner_name", "lines"]
                                }
                            },
                            {
                                "name": "list_invoices",
                                "description": "List recent invoices",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "state": {"type": "string", "enum": ["draft", "posted", "cancel"]},
                                        "limit": {"type": "number"}
                                    }
                                }
                            },
                            {
                                "name": "get_financial_summary",
                                "description": "Get total revenue and expenses",
                                "inputSchema": {"type": "object", "properties": {}}
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool = params.get("name")
                args = params.get("arguments", {})
                
                result = {}
                if tool == "create_invoice":
                    result = client.create_invoice(args.get("partner_name"), args.get("lines"))
                elif tool == "list_invoices":
                    result = client.list_invoices(args.get("state", "posted"), args.get("limit", 10))
                elif tool == "get_financial_summary":
                    result = client.get_financial_summary()
                else:
                    result = {"error": "Tool not found"}

                response = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
            
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            break

if __name__ == "__main__":
    main()
