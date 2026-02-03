import frappe

def execute():
    doctypes = ["Pinjaman Installment", "Pinjaman Pencairan", "Pinjaman"]
    for dt in doctypes:
        print(f"Deleting {dt}...")
        frappe.db.delete(dt)
    
    frappe.db.commit()
    print("All Pinjaman data cleaned.")
