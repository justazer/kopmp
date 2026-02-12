import frappe
from frappe.model.document import Document

class PinjamanProduk(Document):
	pass


@frappe.whitelist(allow_guest=True)
def get_all_pinjaman_produk():
	"""
	Fetch all Pinjaman Produk records.
	"""
	products = frappe.get_all("Pinjaman Produk", 
		fields=["name", "tipe", "admin_fee", "start_date", "end_date", "status"]
	)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = products

@frappe.whitelist(allow_guest=True)
def get_pinjaman_produk_top(pinjaman_produk_id):
	"""
	Fetch Pinjaman Produk Top (tenors) for a specific Pinjaman Produk.
	"""
	tops = frappe.get_all("Pinjaman Produk Top",
		filters={"pinjaman_produk_id": pinjaman_produk_id},
		fields=["name", "top", "rate"]
	)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = tops

@frappe.whitelist(allow_guest=True)
def create_pinjaman_produk(tipe, admin_fee, start_date, end_date, status="Active"):
	"""
	Create a new Pinjaman Produk.
	"""
	try:
		doc = frappe.get_doc({
			"doctype": "Pinjaman Produk",
			"tipe": tipe,
			"admin_fee": admin_fee,
			"start_date": start_date,
			"end_date": end_date,
			"status": status
		})
		doc.insert(ignore_permissions=True)
		
		frappe.response["message"] = "success"
		frappe.response["data"] = doc
	except Exception as e:
		frappe.log_error(f"Error creating product: {str(e)}", "Create Pinjaman Produk API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)

@frappe.whitelist(allow_guest=True)
def update_pinjaman_produk(pinjaman_produk_id, tipe=None, admin_fee=None, start_date=None, end_date=None, status=None):
	"""
	Update an existing Pinjaman Produk.
	"""
	try:
		doc = frappe.get_doc("Pinjaman Produk", pinjaman_produk_id)
		
		if tipe: doc.tipe = tipe
		if admin_fee: doc.admin_fee = admin_fee
		if start_date: doc.start_date = start_date
		if end_date: doc.end_date = end_date
		if status: doc.status = status
		
		doc.save(ignore_permissions=True)
		
		frappe.response["message"] = "success"
		frappe.response["data"] = doc
	except Exception as e:
		frappe.log_error(f"Error updating product: {str(e)}", "Update Pinjaman Produk API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)

@frappe.whitelist(allow_guest=True)
def toggle_status_pinjaman_produk(pinjaman_produk_id):
	"""
	Toggle status of Pinjaman Produk (Active <-> Inactive).
	"""
	try:
		doc = frappe.get_doc("Pinjaman Produk", pinjaman_produk_id)
		
		if doc.status == "Active":
			doc.status = "Inactive"
		else:
			doc.status = "Active"
			
		doc.save(ignore_permissions=True)
		
		frappe.response["message"] = "success"
		frappe.response["data"] = doc

	except Exception as e:
		frappe.log_error(f"Error toggling product status: {str(e)}", "Toggle Product Status API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)

@frappe.whitelist(allow_guest=True)
def create_pinjaman_produk_top(pinjaman_produk_id, top, rate):
	"""
	Create a new Pinjaman Produk Top (Tenor).
	"""
	try:
		# Verify product exists
		if not frappe.db.exists("Pinjaman Produk", pinjaman_produk_id):
			frappe.response["message"] = "error"
			frappe.response["data"] = f"Pinjaman Produk {pinjaman_produk_id} not found"
			return

		doc = frappe.get_doc({
			"doctype": "Pinjaman Produk Top",
			"pinjaman_produk_id": pinjaman_produk_id,
			"top": top,
			"rate": rate
		})
		doc.insert(ignore_permissions=True)
		
		frappe.response["message"] = "success"
		frappe.response["data"] = doc
	except Exception as e:
		frappe.log_error(f"Error creating product top: {str(e)}", "Create Pinjaman Produk Top API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)

@frappe.whitelist(allow_guest=True)
def update_pinjaman_produk_top(pinjaman_produk_top_id, top=None, rate=None):
	"""
	Update an existing Pinjaman Produk Top (Tenor).
	"""
	try:
		doc = frappe.get_doc("Pinjaman Produk Top", pinjaman_produk_top_id)
		
		if top: doc.top = top
		if rate: doc.rate = rate
		
		doc.save(ignore_permissions=True)
		
		frappe.response["message"] = "success"
		frappe.response["data"] = doc
	except Exception as e:
		frappe.log_error(f"Error updating product top: {str(e)}", "Update Pinjaman Produk Top API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)

