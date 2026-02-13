import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class SimpananWajibTagihan(Document):
	pass


@frappe.whitelist(allow_guest=True)
def pay_simpanan_wajib_tagihan(tagihan_id):
	"""
	Pay a Simpanan Wajib Tagihan.
	
	1. Set paid_date on the tagihan
	2. Pay the linked Sales Invoice via Payment Entry
	3. Create Simpanan Wajib Log (saldo_awal, saldo_akhir)
	4. Update saldo on Simpanan Wajib
	
	Args:
		tagihan_id (str): Name of the Simpanan Wajib Tagihan
	"""
	original_user = frappe.session.user
	frappe.set_user("Administrator")
	
	try:
		return _process_payment(tagihan_id)
	finally:
		frappe.set_user(original_user)

def _process_payment(tagihan_id):
	tagihan = frappe.get_doc("Simpanan Wajib Tagihan", tagihan_id)
	
	if tagihan.paid_date:
		frappe.throw(f"Tagihan {tagihan_id} sudah dibayar pada {tagihan.paid_date}")
	
	# 1. Set paid_date
	tagihan.paid_date = nowdate()
	tagihan.save(ignore_permissions=True)
	
	# 2. Find and pay linked Sales Invoice
	invoice_name = frappe.db.get_value(
		"Sales Invoice",
		{"custom_simpanan_wajib_id": tagihan.simpanan_wajib_id, "docstatus": 1},
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
	
	# 3. Create Simpanan Wajib Log
	simpanan_wajib = frappe.get_doc("Simpanan Wajib", tagihan.simpanan_wajib_id)
	saldo_awal = simpanan_wajib.saldo or 0
	saldo_akhir = saldo_awal + tagihan.nominal
	
	log = frappe.new_doc("Simpanan Wajib Log")
	log.simpanan_wajib_id = tagihan.simpanan_wajib_id
	log.nominal = tagihan.nominal
	log.saldo_awal = saldo_awal
	log.saldo_akhir = saldo_akhir
	log.insert(ignore_permissions=True)
	
	# 4. Update saldo on Simpanan Wajib
	simpanan_wajib.saldo = saldo_akhir
	simpanan_wajib.save(ignore_permissions=True)
	
	frappe.db.commit()
	
	frappe.response["message"] = "success"
	frappe.response["data"] = {
		"tagihan_id": tagihan_id,
		"paid_date": str(tagihan.paid_date),
		"nominal": tagihan.nominal,
		"simpanan_wajib_id": tagihan.simpanan_wajib_id,
		"saldo_awal": saldo_awal,
		"saldo_akhir": saldo_akhir,
		"log_id": log.name
	}
