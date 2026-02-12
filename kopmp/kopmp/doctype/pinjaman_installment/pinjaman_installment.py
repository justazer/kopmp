# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.utils import nowdate
from frappe.model.document import Document

class PinjamanInstallment(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.id = make_autoname("PJI-.#####")

	@frappe.whitelist(allow_guest=True)
	def set_paid(self):
		"""
		Mark installment as paid and update linked invoice
		"""
		# 1. Update Installment Fields
		self.payment_status = "Paid"
		self.paid_date = nowdate()
		
		# Set paid amounts equal to nominal amounts (Full Payment Assumption)
		self.paid_pokok = self.nominal_pokok
		self.paid_bunga = self.nominal_bunga
		self.paid_denda = self.nominal_denda or 0
		self.save(ignore_permissions=True)
		
		# Submit to remove "Draft" status
		if self.docstatus == 0:
			self.submit()
		
		# 2. Update Linked Sales Invoice
		if self.installment_invoice:
			invoice = frappe.get_doc("Sales Invoice", self.installment_invoice)
			if invoice.docstatus == 1: # Submitted
				# Force status to 'Paid' (UI fix)
				invoice.db_set('status', 'Paid', update_modified=False)
				# frappe.msgprint(f"Installment {self.name} and Invoice {invoice.name} marked as PAID")
			# else:
				# frappe.msgprint(f"Installment {self.name} marked as PAID (Invoice was not submitted)")

@frappe.whitelist(allow_guest=True)
def pay_installment(installment_id):
	"""
	API Wrapper to mark installment as paid.
	"""
	try:
		doc = frappe.get_doc("Pinjaman Installment", installment_id)
		doc.set_paid()
		
		frappe.response["message"] = "success"
		frappe.response["data"] = doc
	except Exception as e:
		frappe.log_error(f"Error paying installment: {str(e)}", "Pay Installment API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)


@frappe.whitelist(allow_guest=True)
def get_installments(pinjaman_id):
	"""
	Get all installments for a specific Pinjaman ID.
	"""
	if not pinjaman_id:
		frappe.response["message"] = "error"
		frappe.response["data"] = "Pinjaman ID is required"
		return

	data = frappe.get_all("Pinjaman Installment", 
		filters={"pinjaman_id": pinjaman_id},
		fields=["name", "pinjaman_id", "no", "due_date", "nominal_pokok", "nominal_bunga", "nominal_denda", "paid_pokok", "paid_bunga", "paid_denda", "paid_date"],
		order_by="due_date asc"
	)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = data
