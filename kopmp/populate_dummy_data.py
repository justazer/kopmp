import frappe
from frappe.utils import add_days, nowdate
import sys
import os

# Remove the script's directory from sys.path to avoid shadowing the app package
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

# Insert the repo root to sys.path
sys.path.insert(0, os.path.abspath("../apps/kopmp"))



def create_pinjaman_produk():
    products = [
        {
            "id": "PROD-001",
            "tipe": "Pinjaman Konsumtif",
            "admin_fee": 50000,
            "start_date": nowdate(),
            "end_date": add_days(nowdate(), 365),
            "tops": [
                {"top": 3, "rate": 1.5},
                {"top": 6, "rate": 1.75},
                {"top": 12, "rate": 2.0}
            ]
        },
        {
            "id": "PROD-002",
            "tipe": "Pinjaman Produktif",
            "admin_fee": 25000,
            "start_date": nowdate(),
            "end_date": add_days(nowdate(), 365),
            "tops": [
                {"top": 6, "rate": 1.2},
                {"top": 12, "rate": 1.4},
                {"top": 24, "rate": 1.6}
            ]
        },
        {
            "id": "PROD-003",
            "tipe": "Pinjaman Syariah",
            "admin_fee": 75000,
            "start_date": nowdate(),
            "end_date": add_days(nowdate(), 365),
            "tops": [
                {"top": 12, "rate": 0.5}, 
                {"top": 24, "rate": 0.5}
            ]
        }
    ]

    for p in products:
        if not frappe.db.exists("Pinjaman Produk", {"id": p["id"]}):
            doc = frappe.get_doc({
                "doctype": "Pinjaman Produk",
                "id": p["id"],
                "tipe": p["tipe"],
                "admin_fee": p["admin_fee"],
                "start_date": p["start_date"],
                "end_date": p["end_date"]
            })
            doc.insert()
            print(f"Created Pinjaman Produk: {p['id']}")
        else:
             print(f"Pinjaman Produk {p['id']} already exists.")

        # Create TOPs
        for t in p["tops"]:
            top_id = f"{p['id']}-TOP-{t['top']}"
            if not frappe.db.exists("Pinjaman Produk Top", {"id": top_id}):
                try:
                    top_doc = frappe.get_doc({
                        "doctype": "Pinjaman Produk Top",
                        "id": top_id,
                        "pinjaman_produk_id": p["id"],
                        "top": t["top"],
                        "rate": t["rate"]
                    })
                    top_doc.insert()
                    print(f"  Created TOP: {t['top']} months for {p['id']}")
                except Exception as e:
                    print(f"  Failed to create TOP {t['top']} for {p['id']}: {e}")
            else:
                print(f"  TOP {t['top']} for {p['id']} already exists.")

    frappe.db.commit()

def run():
    try:
        frappe.init(site="mysite.localhost")
        frappe.connect()
        create_pinjaman_produk()
    finally:
        if frappe.db:
            frappe.destroy()

if __name__ == "__main__":
    run()
