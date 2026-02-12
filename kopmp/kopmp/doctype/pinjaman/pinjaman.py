# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Pinjaman(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.id = make_autoname("PJN-.#####")

	def after_insert(self):
		produk = frappe.get_doc("Pinjaman Produk", self.pinjaman_produk_id)
		pencairan = frappe.new_doc("Pinjaman Pencairan")
		pencairan.pinjaman_id = self.name
		pencairan.nominal = self.nominal - produk.admin_fee
		pencairan.status = "Requested"
		pencairan.request_at = self.request_at
		pencairan.approved_at = None
		pencairan.insert(ignore_permissions=True)
		
		# Create disbursement invoice immediately
		self.create_disbursement_invoice(pencairan)

		# Send Email Notification
		email = frappe.db.get_value("User Profile", self.profile_id, "email")
		# if email:
		# 	subject = f"Pinjaman Created: {self.name}"
		# 	message = f"Dear User,<br><br>Your Pinjaman application {self.name} for {self.nominal} has been created and is currently Requested.<br><br>Thank you."
		# 	frappe.sendmail(recipients='reza.baharsyah@indocyber.id', subject=subject, message=message, sender='Koperasi App <no-reply@brevosend.com>' ,delayed=False)
	
	def create_disbursement_invoice(self, pinjaman_pencairan):
		"""Create disbursement invoice (as draft/unpaid)"""
		from kopmp.utils.invoice import create_disbursement_invoice
		
		try:
			invoice_name = create_disbursement_invoice(pinjaman_pencairan)
			
			# Store reference in Pinjaman Pencairan
			pinjaman_pencairan.db_set('disbursement_invoice', invoice_name, update_modified=False)
			
			frappe.logger().info(f"Created disbursement invoice {invoice_name} for Pinjaman {self.name}")
			
		except Exception as e:
			frappe.log_error(f"Error creating disbursement invoice: {str(e)}", "Pinjaman Invoice Creation")
			# Don't throw - allow Pinjaman creation to succeed even if invoice fails

@frappe.whitelist(allow_guest=True)
def create_pinjaman(profile_id, pinjaman_produk_id, nominal, top, rate, start_date, end_date):
	"""
	API to create a new Pinjaman (Loan) application.
	
	Args:
		profile_id (str): User Profile ID
		pinjaman_produk_id (str): Pinjaman Produk ID
		nominal (float): Loan Amount
		top (str): Term of Payment
		rate (float): Interest Rate
		start_date (str): Start Date (YYYY-MM-DD)
		end_date (str): End Date (YYYY-MM-DD)
	
	Returns:
		dict: Created Pinjaman document
	"""
	try:
		pinjaman = frappe.get_doc({
			"doctype": "Pinjaman",
			"profile_id": profile_id,
			"pinjaman_produk_id": pinjaman_produk_id,
			"nominal": nominal,
			"top": top,
			"rate": rate,
			"start_date": start_date,
			"end_date": end_date,
			"request_at": frappe.utils.now_datetime(),
			"status": "Requested"
		})
		
		pinjaman.insert(ignore_permissions=True)
		
		frappe.response["message"] = "success"
		frappe.response["data"] = pinjaman
	except Exception as e:
		frappe.log_error(f"Error creating pinjaman: {str(e)}", "Create Pinjaman API")
		# frappe.throw(f"Failed to create pinjaman: {str(e)}") # Optional: throw to return 500
		raise e

@frappe.whitelist(allow_guest=True)
def get_pinjaman(profile_id=None):
	"""
	Get all Pinjaman applications for a specific User Profile.
	"""
	if(profile_id != None and profile_id.strip() != ""):
		data = frappe.get_all("Pinjaman", 
			filters={"profile_id": profile_id},
			fields=["name", "pinjaman_produk_id", "nominal", "status", "request_at", "approved_at", "start_date", "end_date", "rate", "top"],
			order_by="creation desc"
		)
	else:
		data = frappe.get_all("Pinjaman", 
			fields=["name", "pinjaman_produk_id", "nominal", "status", "request_at", "approved_at", "start_date", "end_date", "rate", "top","profile_id"],
			order_by="creation desc"
		)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = data


@frappe.whitelist(allow_guest=True)
def process_pinjaman(pinjaman_id, action):
	"""
	Process Pinjaman application (Approve or Reject).
	Action: 'approved' | 'reject'
	"""
	try:
		pinjaman = frappe.get_doc("Pinjaman", pinjaman_id)
		
		# Validation
		if pinjaman.status != "Requested":
			frappe.response["message"] = "error"
			frappe.response["data"] = f"Pinjaman status is {pinjaman.status}, cannot process."
			return

		action_lower = action.lower() if action else ""

		if action_lower in ["approved", "approve"]:
			# Approve Logic
			pinjaman.status = "Approved"
			pinjaman.approved_at = frappe.utils.now_datetime()
			pinjaman.save(ignore_permissions=True)
			pinjaman.submit()
			
			frappe.response["message"] = "success"
			frappe.response["data"] = pinjaman

		elif action_lower in ["reject", "rejected"]:
			# Reject Logic
			pinjaman.status = "Rejected"
			pinjaman.save(ignore_permissions=True)
			
			frappe.response["message"] = "success"
			frappe.response["data"] = pinjaman

		else:
			frappe.response["message"] = "error"
			frappe.response["data"] = f"Invalid action: {action}. Use 'approved' or 'reject'."
		
	except Exception as e:
		frappe.log_error(f"Error processing pinjaman: {str(e)}", "Process Pinjaman API")
		frappe.response["message"] = "error"
		frappe.response["data"] = str(e)



@frappe.whitelist(allow_guest=True)
def get_list_kontrak_pinjaman(profile_id=None):
	"""
	Get all Approved Pinjaman applications that have outstanding installments.
	Optionally filter by profile_id.
	"""
	query = """
		SELECT 
			p.name, p.profile_id, p.pinjaman_produk_id, p.nominal, p.status, 
			p.request_at, p.approved_at, p.start_date, p.end_date, p.rate, p.top
		FROM 
			`tabPinjaman` p
		WHERE 
			p.status = 'Approved'
			AND EXISTS (
				SELECT 1 FROM `tabPinjaman Installment` pi 
				WHERE pi.pinjaman_id = p.name 
				AND (pi.paid_pokok < pi.nominal_pokok OR pi.paid_bunga < pi.nominal_bunga)
			)
	"""
	
	params = {}
	if profile_id:
		query += " AND p.profile_id = %(profile_id)s"
		params["profile_id"] = profile_id
		
	query += " ORDER BY p.approved_at DESC"
		
	data = frappe.db.sql(query, params, as_dict=True)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = data


