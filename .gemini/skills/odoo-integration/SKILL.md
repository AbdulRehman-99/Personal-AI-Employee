# Odoo Integration Skill

## Overview
This skill integrates Odoo 17 (Community Edition) with the Personal AI Employee.
It provides:
- Automated accounting actions via MCP (Create Invoice, Register Payment).
- Financial monitoring via a Watcher script.
- CEO Briefing data source.

## Prerequisites
1. **Docker & Docker Compose**: Must be installed and running.
2. **Odoo Instance**: Run `docker-compose up -d` in the project root.
3. **Database Setup**:
   - Go to `http://localhost:8069`
   - Create a database (Master Password: `admin` by default, or check logs).
   - Install **Invoicing** and **Accounting** (if available) modules.
   - **CRITICAL**: Create a user for the bot (or use admin) and get the **API Key** if using 17+, or just password.

## Configuration
Create a `.env` file or set environment variables:
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=your_database_name
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password
```

## Tools (MCP)
- `create_invoice`: Creates a customer invoice.
- `register_payment`: Registers a payment for an invoice.
- `get_financial_summary`: Returns revenue, expenses, and pending invoices.

## Watcher
- `finance_watcher.py`: Checks for overdue invoices and large transactions.
