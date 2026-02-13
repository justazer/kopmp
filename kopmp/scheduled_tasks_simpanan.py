import frappe
from frappe.utils import nowdate, getdate, get_first_day
from kopmp.utils.customer import get_or_create_customer
from kopmp.utils.invoice import get_default_cost_center


def create_monthly_simpanan_wajib_tagihan():
	"""
	Scheduler: Runs daily, but only creates tagihan on the 1st of each month.
	Creates a Simpanan Wajib Tagihan of 10,000 for every active Simpanan Wajib,
	along with a corresponding Sales Invoice.
	"""
	today = getdate(nowdate())
	
	# Only run on the 1st of the month
	if today.day != 1:
		return
	
	frappe.logger().info("Running monthly Simpanan Wajib Tagihan creation...")
	
	# Get all Simpanan Wajib
	simpanan_list = frappe.get_all("Simpanan Wajib", fields=["name", "profile_id"])
	
	company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		frappe.logger().error("No default company set, skipping Simpanan Wajib Tagihan creation")
		return
	
	count = 0
	for sw in simpanan_list:
		try:
			# Create Tagihan
			tagihan = frappe.new_doc("Simpanan Wajib Tagihan")
			tagihan.simpanan_wajib_id = sw.name
			tagihan.nominal = 10000
			tagihan.due_date = nowdate()
			tagihan.insert(ignore_permissions=True)
			
			# Create Sales Invoice
			customer = get_or_create_customer(sw.profile_id)
			
			income_account = frappe.db.get_value("Account", {"account_name": "Simpanan Wajib", "company": company, "is_group": 0}, "name")
			if not income_account:
				income_account = frappe.db.get_value("Company", company, "default_income_account")
			if not income_account:
				income_account = frappe.db.get_value("Account", {"account_name": "Sales", "company": company, "is_group": 0}, "name")
			
			invoice = frappe.new_doc("Sales Invoice")
			invoice.customer = customer
			invoice.posting_date = nowdate()
			invoice.due_date = nowdate()
			invoice.company = company
			invoice.custom_simpanan_wajib_id = sw.name
			invoice.custom_invoice_type = "Simpanan Wajib Tagihan"
			
			invoice.append("items", {
				"item_code": "SIMPANAN-WAJIB",
				"item_name": "Simpanan Wajib Bulanan",
				"description": f"Simpanan Wajib Bulanan {today.strftime('%B %Y')} for {sw.name}",
				"qty": 1,
				"rate": 10000,
				"income_account": income_account,
				"cost_center": get_default_cost_center(company)
			})
			
			invoice.insert(ignore_permissions=True)
			invoice.submit()
			
			count += 1
		except Exception as e:
			frappe.log_error(f"Error creating Simpanan Wajib Tagihan for {sw.name}: {e}")
	
	frappe.db.commit()
	frappe.logger().info(f"Created {count} Simpanan Wajib Tagihan for {today.strftime('%B %Y')}")
