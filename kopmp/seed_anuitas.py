import frappe

def execute():
    if not frappe.db.exists("Pinjaman Produk", "Pinjaman Anuitas"):
        # Create Pinjaman Anuitas
        doc = frappe.new_doc("Pinjaman Produk")
        doc.id = "Pinjaman Anuitas"
        doc.tipe = "Anuitas"
        doc.admin_fee = 0 # Default, can be updated
        doc.start_date = "2024-01-01"
        doc.end_date = "2030-12-31"
        doc.insert()
        print("Created Pinjaman Anuitas")
    
    # Ensure TOP 12 exists for it
    if not frappe.db.exists("Pinjaman Produk Top", {"pinjaman_produk_id": "Pinjaman Anuitas", "top": "12"}):
        top_doc = frappe.new_doc("Pinjaman Produk Top")
        top_doc.id = "Pinjaman Anuitas-12"
        top_doc.pinjaman_produk_id = "Pinjaman Anuitas"
        top_doc.top = "12"
        top_doc.rate = 12.0 # 12% Annual Rate (Example)
        top_doc.insert()
        print("Created TOP 12 for Pinjaman Anuitas")
    
    frappe.db.commit()
