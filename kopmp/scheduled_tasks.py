import frappe
from frappe.utils import getdate, nowdate, date_diff

def update_denda_harian():
    """
    Checks all Pinjaman Installment records.
    If due_date < today AND paid_date is not set,
    update nominal_denda = days_overdue * 100,000.
    """
    today = getdate(nowdate())
    
    # Fetch overdue installments that are not paid (paid_date is None)
    overdue_installments = frappe.get_all("Pinjaman Installment", 
        filters={
            "due_date": ["<", today],
            "paid_date": ["is", "not set"]
        }
    )

    for d in overdue_installments:
        doc = frappe.get_doc("Pinjaman Installment", d.name)
        
        days_overdue = date_diff(today, doc.due_date)
        
        if days_overdue > 0:
            new_denda = days_overdue * 100000
            if doc.nominal_denda != new_denda:
                doc.nominal_denda = new_denda
                doc.save()
                frappe.db.commit()
