import frappe
from frappe.utils import add_days, nowdate
import sys
import os


# Remove the script's directory from sys.path to avoid shadowing the app package
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)




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

def create_user_profiles():
    profiles = [
        {
            "id": "USR-001",
            "user_name": "Budi Santoso",
            "phone": "081234567890",
            "address": "Jl. Merdeka No. 1, Jakarta",
            "email": "budi.santoso@example.com",
            "status": "Active"
        },
        {
            "id": "USR-002",
            "user_name": "Siti Aminah",
            "phone": "081987654321",
            "address": "Jl. Kebon Jeruk No. 10, Jakarta",
            "email": "siti.aminah@example.com",
            "status": "Active"
        },
        {
            "id": "USR-003",
            "user_name": "Ahmad Dani",
            "phone": "085678912345",
            "address": "Jl. Diponegoro No. 5, Surabaya",
            "email": "ahmad.dani@example.com",
            "status": "Inactive"
        }
    ]

    for p in profiles:
        if not frappe.db.exists("User Profile", {"id": p["id"]}):
            doc = frappe.get_doc({
                "doctype": "User Profile",
                "id": p["id"],
                "user_name": p["user_name"],
                "phone": p["phone"],
                "address": p["address"],
                "email": p["email"],
                "status": p["status"]
            })
            doc.insert()
            print(f"Created User Profile: {p['id']}")
        else:
            print(f"User Profile {p['id']} already exists.")

    frappe.db.commit()


def run():
    try:
        print(f"DEBUG: CWD: {os.getcwd()}")
        if os.path.exists("sites"):
            print("DEBUG: 'sites' directory found.")
            print(f"DEBUG: 'sites' content: {os.listdir('sites')}")
        else:
            print("DEBUG: 'sites' directory NOT found.")
        
        # Change directory to 'sites' to simplify path resolution for frappe
        if os.path.exists("sites"):
            os.chdir("sites")
            print(f"DEBUG: Changed CWD to: {os.getcwd()}")
        else:
             print("DEBUG: 'sites' directory not found in CWD, assuming we are already there or path is wrong.")

        frappe.init(site="erpnext.local")
        frappe.connect()
        create_pinjaman_produk()
        create_user_profiles()
    finally:
        if frappe.db:
            frappe.destroy()


if __name__ == "__main__":
    run()
