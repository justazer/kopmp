import frappe
from frappe.model.document import Document

class PinjamanProduk(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_all_data():
	"""
	Fetch all Pinjaman Produk records and include their related Pinjaman Produk Top (tenors).
	"""
	products = frappe.get_all("Pinjaman Produk", 
		fields=["name", "tipe", "admin_fee", "start_date", "end_date"]
	)
	
	for product in products:
		product["tops"] = frappe.get_all("Pinjaman Produk Top",
			filters={"pinjaman_produk_id": product.name},
			fields=["name", "top", "rate"]
		)
		
	return products
