# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, get_first_day
from dateutil.relativedelta import relativedelta

class PinjamanPencairan(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.id = make_autoname("PCN-.#####")

	def on_submit(self):
		if self.status == 'Disbursed' or self.status == 'Approved': # Handling potentially different approved statuses
			# Create installments first
			self.create_installments()
			
			# Create invoices
			self.create_invoices()

	def create_installments(self):
		pinjaman = frappe.get_doc("Pinjaman", self.pinjaman_id)
		produk = frappe.get_doc("Pinjaman Produk", pinjaman.pinjaman_produk_id)
		
		# Common Variables
		nominal = float(pinjaman.nominal)
		rate_percent = float(pinjaman.rate)
		top = int(pinjaman.top)
		admin_fee = float(produk.admin_fee or 0)
		
		start_date = getdate(self.approved_at) or getdate()
		next_month = start_date + relativedelta(months=1)
		current_due_date = get_first_day(next_month)

		if produk.tipe == "Anuitas":
			# --- Annuity Logic (PMT) ---
			monthly_rate = (rate_percent / 100) / 12
			
			if monthly_rate > 0:
				pmt = (nominal * monthly_rate) / (1 - (1 + monthly_rate) ** -top)
			else:
				pmt = nominal / top
			
			# Admin Fee per month (User requested no division, implying monthly fee)
			monthly_admin_fee = admin_fee 
			remaining_principal = nominal
			
			for i in range(1, top + 1):
				interest_payment = remaining_principal * monthly_rate
				principal_payment = pmt - interest_payment
				
				# Adjust last installment
				if i == top:
					principal_payment = remaining_principal
				
				remaining_principal -= principal_payment
				
				doc = frappe.new_doc("Pinjaman Installment")
				doc.pinjaman_id = self.pinjaman_id
				doc.no = i
				doc.due_date = current_due_date
				doc.nominal_pokok = principal_payment
				doc.nominal_bunga = interest_payment
				doc.insert()
				
				current_due_date = current_due_date + relativedelta(months=1)

		else:
			# --- Standard Flat Logic ---
			# Nominal Pokok includes Principal only
			nominal_pokok = (nominal / top)
			nominal_bunga = nominal * (rate_percent / 100)

			for i in range(1, top + 1):
				doc = frappe.new_doc("Pinjaman Installment")
				doc.pinjaman_id = self.pinjaman_id
				doc.no = i
				doc.due_date = current_due_date
				doc.nominal_pokok = nominal_pokok
				doc.nominal_bunga = nominal_bunga
				doc.insert(ignore_permissions=True)
				
				current_due_date = current_due_date + relativedelta(months=1)


	def create_invoices(self):
		"""
		Submit disbursement invoice and create installment invoices
		"""
		from kopmp.utils.invoice import create_installment_invoices
		
		try:
			# Submit the existing disbursement invoice (created when Pinjaman was created)
			if self.disbursement_invoice:
				invoice = frappe.get_doc("Sales Invoice", self.disbursement_invoice)
				if invoice.docstatus == 0:  # If still draft
					invoice.flags.ignore_permissions = True
					invoice.submit()
					
					# Force status to 'Paid' to indicate Disbursement Complete (UI fix)
					invoice.db_set('status', 'Paid', update_modified=False)
					
					frappe.logger().info(f"Submitted disbursement invoice {invoice.name}")
			else:
				frappe.msgprint("Warning: No disbursement invoice found to submit", indicator="orange")
			
			# Create installment invoices
			installment_invoices = create_installment_invoices(self.pinjaman_id)
			
			frappe.msgprint(
				f"Disbursement approved! Created {len(installment_invoices)} installment invoices"
			)
			
		except Exception as e:
			frappe.log_error(f"Error processing invoices: {str(e)}", "Pinjaman Invoice Creation")
			frappe.msgprint(f"Warning: Failed to process invoices. Error: {str(e)}", indicator="orange")

@frappe.whitelist(allow_guest=True)
def get_pencairan_by_pinjaman(pinjaman_id=None):
	"""
	Get Pinjaman Pencairan data. 
	If pinjaman_id is provided, filter by it. If not found, return "not found".
	If not provided, return all.
	"""
	filters = {}
	if pinjaman_id:
		filters["pinjaman_id"] = pinjaman_id

	data = frappe.get_all("Pinjaman Pencairan", 
		filters=filters,
		fields=["name", "pinjaman_id", "nominal", "status", "request_at", "approved_at"],
		order_by="creation desc"
	)
	
	if pinjaman_id and not data:
		frappe.response["message"] = "not found"
		frappe.response["data"] = []

	else:
		frappe.response["message"] = "success"
		frappe.response["data"] = data


@frappe.whitelist(allow_guest=True)
def process_pencairan(pencairan_id, action):
	"""
	Process Pinjaman Pencairan application (Approve or Reject).
	Action: 'approved' | 'reject'
	"""
	try:
		pencairan = frappe.get_doc("Pinjaman Pencairan", pencairan_id)
		
		# Validation
		if pencairan.status != "Requested":
			frappe.response["message"] = "error"
			frappe.response["data"] = f"Pencairan status is {pencairan.status}, cannot process."
			return

		action_lower = action.lower() if action else ""

		if action_lower in ["approved", "approve"]:
			# Approve Logic
			pencairan.status = "Approved"
			pencairan.approved_at = frappe.utils.now_datetime()
			pencairan.save(ignore_permissions=True)
			pencairan.submit()
			
			frappe.response["message"] = "success"
			frappe.response["data"] = pencairan

		elif action_lower in ["reject", "rejected"]:
			# Reject Logic
			pencairan.status = "Rejected"
			pencairan.save(ignore_permissions=True)
			
			frappe.response["message"] = "success"
			frappe.response["data"] = pencairan

		else:
			frappe.response["message"] = "error"
			frappe.response["data"] = f"Invalid action: {action}. Use 'approved' or 'reject'."
		
	except Exception as e:
		frappe.log_error(f"Error processing pencairan: {str(e)}", "Process Pencairan API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)
