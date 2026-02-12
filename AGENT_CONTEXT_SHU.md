# 🤖 AI Agent Context: ERPNext Integration Interface

**Objective:** Provide a standardized interface for custom modules to interact with ERPNext Accounting (Invoices & Payments).
**App Name:** `koperasiapp`

This context defines the **Accounting Integration Layer**. Your task is to use these patterns to implement the specific business logic (SHU, Loans, etc.) as directed by the user.

---

## 🔌 Integration Interface (The Toolbox)

You have access to the following architectural patterns. Do not reinvent them; use them to ensure consistency.

### 1. Customer Management (`utils/customer.py`)
**Role:** Ensure every cooperative member has a corresponding `Customer` entity in ERPNext for accounting purposes.

**Pattern to Implement:**
```python
def get_or_create_customer(user_profile_id):
    """
    1. Check if 'User Profile' linked to a Customer.
    2. If not, create a new Customer document.
    3. Return the Customer Name.
    """
    # Use this to fill 'invoice.customer'
```

### 2. Invoice Generation (`utils.invoice` pattern)
**Role:** Create **Draft** Sales Invoices from operational documents.

**Pattern to Implement:**
Create a wrapper function `create_invoice(source_doc)` that:
1.  Resolves the Customer (using Step 1).
2.  Creates a `Sales Invoice` object.
3.  Maps items (Service/Product) -> Invoice Items.
4.  **Important:** Sets `custom_source_id` (or similar) on the Invoice to link back to your Source Doc.
5.  Inserts as **Draft**.

### 3. Submission & Locking
**Role:** The Accounting Entry (Invoice) should only be finalized when the Operational Doc is finalized.

**Pattern:**
- **Trigger:** `on_submit` of your Source Doc.
- **Action:** Fetch the Draft Invoice -> Call `.submit()` -> Call `.db_set('status', 'Paid')` (if applicable).

### 4. Payment Status Sync
**Role:** If an Invoice is paid via standard ERPNext "Payment Entry", update the Source Doc.

**Pattern:**
- **Hook:** Listen to `on_submit` of `Payment Entry`.
- **Logic:** Trace Payment -> Invoice -> Source Doc. Update Source Doc status.

---

## � Pre-Requisites (Setup)

Before running logic, ensure the generic accounting master data exists.

**Setup Script Pattern (`setup_integration.py`):**
- Check/Create **Item Groups** (e.g., "Services").
- Check/Create **Items** (e.g., "Admin Fee", "Distribution Service").
- Check/Create **Accounts** (Income/Expense ledgers).

---

## 📝 Rules for the Agent

1.  **Separation of Concerns:** Keep accounting logic (Invoices) separate from business logic (Calculations).
2.  **Idempotency:** Invoice creation should check if an invoice already links to the source doc to prevent duplicates.
3.  **Error Handling:** If Invoice submission fails, the Source Doc submission should also fail (Atomic Transaction).
4.  **Use `koperasiapp` namespace:** All utilities should reside within the app package.

---
*Use this context to build the accounting bridge for any new module.*
