import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from kopmp.utils.customer import get_or_create_customer
from kopmp.utils.invoice import get_default_cost_center
from frappe import _

class SimpananPokok(Document):
	def after_insert(self):
		self.create_tagihan()
		self.create_invoice()

	def create_tagihan(self):
		doc = frappe.new_doc("Simpanan Pokok Tagihan")
		doc.simpanan_pokok_id = self.name
		doc.nominal = 250000
		doc.due_date = nowdate()
		doc.insert(ignore_permissions=True)

	def create_invoice(self):
		# Get default company
		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
		if not company:
			return

		customer = get_or_create_customer(self.profile_id)
		
		# Create Sales Invoice
		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = customer
		invoice.posting_date = nowdate()
		invoice.due_date = nowdate()
		invoice.company = company
		
		# Set custom fields
		invoice.custom_simpanan_pokok_id = self.name
		invoice.custom_invoice_type = "Simpanan Pokok Tagihan"
		
		# Item
		invoice.append("items", {
			"item_code": "SIMPANAN-POKOK",
			"item_name": "Simpanan Pokok Initial",
			"description": f"Simpanan Pokok for {self.name}",
			"qty": 1,
			"rate": 250000,
			"income_account": self.get_income_account(company),
			"cost_center": get_default_cost_center(company)
		})
		
		invoice.insert(ignore_permissions=True)
		invoice.submit()

	def get_income_account(self, company):
		# Try to find a specific account or default to Sales
		account = frappe.db.get_value("Account", {"account_name": "Simpanan Pokok", "company": company, "is_group": 0}, "name")
		if not account:
			# Fallback to default income account
			account = frappe.db.get_value("Company", company, "default_income_account")
		
		if not account:
			# Fallback to a generic Sales account
			account = frappe.db.get_value("Account", {"account_name": "Sales", "company": company, "is_group": 0}, "name")
			
		return account


@frappe.whitelist(allow_guest=True)
def get_detail(profile_id):
	"""
	Get Simpanan Pokok detail for a user profile.
	
	Args:
		profile_id (str): User Profile ID
		
	Returns:
		dict: Simpanan Pokok detail with saldo and tagihan list
	"""
	simpanan = frappe.db.get_value(
		"Simpanan Pokok",
		{"profile_id": profile_id},
		["name", "profile_id", "saldo", "creation"],
		as_dict=True
	)
	
	if not simpanan:
		frappe.response["message"] = "not_found"
		frappe.response["data"] = None
		return
	
	frappe.response["message"] = "success"
	frappe.response["data"] = simpanan


@frappe.whitelist(allow_guest=True)
def get_detail_by_id(simpanan_pokok_id):
	"""
	Get Simpanan Pokok detail by its ID.
	
	Args:
		simpanan_pokok_id (str): Simpanan Pokok ID (e.g. SIMPK-00001)
		
	Returns:
		dict: Simpanan Pokok detail
	"""
	simpanan = frappe.db.get_value(
		"Simpanan Pokok",
		simpanan_pokok_id,
		["name", "profile_id", "saldo", "creation"],
		as_dict=True
	)
	
	if not simpanan:
		frappe.response["message"] = "not_found"
		frappe.response["data"] = None
		return
	
	frappe.response["message"] = "success"
	frappe.response["data"] = simpanan


@frappe.whitelist(allow_guest=True)
def get_list():
	"""
	Get list of all Simpanan Pokok anggota.
	
	Returns:
		list: All Simpanan Pokok records with profile info
	"""
	data = frappe.get_all(
		"Simpanan Pokok",
		fields=["name", "profile_id", "saldo", "creation"],
		order_by="creation desc"
	)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = data
