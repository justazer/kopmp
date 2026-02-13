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
	Get installments for a specific Pinjaman ID.
	Filter:
	1. All past unpaid installments (Arrears) with docstatus=1
	2. Next month's installment ONLY IF today's date > 20
	"""
	from frappe.utils import getdate, nowdate, add_months
	
	if not pinjaman_id:
		frappe.response["message"] = "error"
		frappe.response["data"] = "Pinjaman ID is required"
		return

	# Get all submitted installments sorted by date
	all_installments = frappe.get_all("Pinjaman Installment", 
		filters={"pinjaman_id": pinjaman_id},
		fields=["name", "pinjaman_id", "no", "due_date", "nominal_pokok", "nominal_bunga", "nominal_denda", "paid_pokok", "paid_bunga", "paid_denda", "paid_date"],
		order_by="due_date asc"
	)
	
	today = getdate(nowdate())
	result = []
	
	next_month = add_months(today, 1)
	# Next month 1st date
	next_month_1st = getdate(f"{next_month.year}-{next_month.month:02d}-01")
	
	for inst in all_installments:
		due_date = getdate(inst.due_date)
		
		# Overdue Logic: paid_date is None AND today > due_date
		# User said "hari ini lebih besar dari pada due_date" (today > due_date)
		if not inst.paid_date and today > due_date:
			inst["status"] = "Overdue"
			result.append(inst)
			
		# Upcoming Logic: today > 20 AND due_date is 1st of next month
		elif today.day > 20 and not inst.paid_date:
			# Check if due_date is exactly the 1st of next month
			if due_date == next_month_1st:
				inst["status"] = "Upcoming"
				result.append(inst)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = result
