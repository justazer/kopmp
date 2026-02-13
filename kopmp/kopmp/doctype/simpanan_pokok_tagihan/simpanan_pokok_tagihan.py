import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class SimpananPokokTagihan(Document):
	pass


@frappe.whitelist(allow_guest=True)
def pay_simpanan_pokok_tagihan(tagihan_id):
	"""
	Pay a Simpanan Pokok Tagihan.
	
	1. Set paid_date on the tagihan
	2. Pay the linked Sales Invoice via Payment Entry
	3. Update saldo on Simpanan Pokok += nominal
	
	Args:
		tagihan_id (str): Name of the Simpanan Pokok Tagihan
	"""
	original_user = frappe.session.user
	frappe.set_user("Administrator")
	
	try:
		return _process_payment(tagihan_id)
	finally:
		frappe.set_user(original_user)

def _process_payment(tagihan_id):
	tagihan = frappe.get_doc("Simpanan Pokok Tagihan", tagihan_id)
	
	if tagihan.paid_date:
		frappe.throw(f"Tagihan {tagihan_id} sudah dibayar pada {tagihan.paid_date}")
	
	# 1. Set paid_date
	tagihan.paid_date = nowdate()
	tagihan.save(ignore_permissions=True)
	
	# 2. Find and pay linked Sales Invoice
	invoice_name = frappe.db.get_value(
		"Sales Invoice",
		{"custom_simpanan_pokok_id": tagihan.simpanan_pokok_id, "docstatus": 1},
		"name"
	)
	
	if invoice_name:
		invoice = frappe.get_doc("Sales Invoice", invoice_name)
		
		# Create Payment Entry
		company = invoice.company
		payment = frappe.new_doc("Payment Entry")
		payment.payment_type = "Receive"
		payment.party_type = "Customer"
		payment.party = invoice.customer
		payment.company = company
		payment.posting_date = nowdate()
		payment.paid_amount = invoice.outstanding_amount
		payment.received_amount = invoice.outstanding_amount
		payment.target_exchange_rate = 1
		payment.paid_to = frappe.db.get_value("Company", company, "default_cash_account") or frappe.db.get_value("Account", {"account_type": "Cash", "company": company, "is_group": 0}, "name")
		payment.paid_from = frappe.db.get_value("Company", company, "default_receivable_account") or frappe.db.get_value("Account", {"account_type": "Receivable", "company": company, "is_group": 0}, "name")
		
		payment.append("references", {
			"reference_doctype": "Sales Invoice",
			"reference_name": invoice_name,
			"total_amount": invoice.grand_total,
			"outstanding_amount": invoice.outstanding_amount,
			"allocated_amount": invoice.outstanding_amount
		})
		
		payment.insert(ignore_permissions=True)
		payment.submit()
	
	# 3. Update saldo on Simpanan Pokok
	simpanan_pokok = frappe.get_doc("Simpanan Pokok", tagihan.simpanan_pokok_id)
	simpanan_pokok.saldo = (simpanan_pokok.saldo or 0) + tagihan.nominal
	simpanan_pokok.save(ignore_permissions=True)
	
	frappe.db.commit()
	
	frappe.response["message"] = "success"
	frappe.response["data"] = {
		"tagihan_id": tagihan_id,
		"paid_date": str(tagihan.paid_date),
		"nominal": tagihan.nominal,
		"simpanan_pokok_id": tagihan.simpanan_pokok_id,
		"new_saldo": simpanan_pokok.saldo
	}


@frappe.whitelist(allow_guest=True)
def get_tagihan_list(profile_id=None):
	"""
	Get list of all Simpanan tagihan (Pokok + Wajib).
	
	Args:
		profile_id (str, optional): Filter by User Profile ID
		
	Returns:
		list: Combined list of Simpanan Pokok Tagihan and Simpanan Wajib Tagihan
	"""
	result = []
	
	# Simpanan Pokok Tagihan
	sp_filters = {}
	if profile_id:
		sp_ids = frappe.get_all("Simpanan Pokok", filters={"profile_id": profile_id}, pluck="name")
		if sp_ids:
			sp_filters["simpanan_pokok_id"] = ["in", sp_ids]
		else:
			sp_filters["simpanan_pokok_id"] = "NONE"
	
	sp_tagihan = frappe.get_all(
		"Simpanan Pokok Tagihan",
		filters=sp_filters,
		fields=["name", "simpanan_pokok_id", "nominal", "due_date", "paid_date", "creation"]
	)
	for t in sp_tagihan:
		t["type"] = "Simpanan Pokok"
		t["status"] = "Paid" if t.get("paid_date") else "Unpaid"
		result.append(t)
	
	# Simpanan Wajib Tagihan
	sw_filters = {}
	if profile_id:
		sw_ids = frappe.get_all("Simpanan Wajib", filters={"profile_id": profile_id}, pluck="name")
		if sw_ids:
			sw_filters["simpanan_wajib_id"] = ["in", sw_ids]
		else:
			sw_filters["simpanan_wajib_id"] = "NONE"
	
	sw_tagihan = frappe.get_all(
		"Simpanan Wajib Tagihan",
		filters=sw_filters,
		fields=["name", "simpanan_wajib_id", "nominal", "due_date", "paid_date", "creation"]
	)
	for t in sw_tagihan:
		t["type"] = "Simpanan Wajib"
		t["status"] = "Paid" if t.get("paid_date") else "Unpaid"
		result.append(t)
	
	# Sort by creation desc
	result.sort(key=lambda x: x.get("creation", ""), reverse=True)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = result
