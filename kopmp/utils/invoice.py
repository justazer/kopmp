"""
Invoice creation utilities for Pinjaman integration
"""
import frappe
from frappe import _
from frappe.utils import nowdate, getdate
from kopmp.utils.customer import get_or_create_customer


def create_disbursement_invoice(pinjaman_pencairan):
	"""
	Create Sales Invoice for loan disbursement
	
	Args:
		pinjaman_pencairan: Pinjaman Pencairan document
		
	Returns:
		str: Sales Invoice name
	"""
	try:
		# Get related Pinjaman
		pinjaman = frappe.get_doc("Pinjaman", pinjaman_pencairan.pinjaman_id)
		
		# Get or create customer
		customer = get_or_create_customer(pinjaman.profile_id)
		
		# Get default company
		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
		
		if not company:
			frappe.throw(_("Please set a default company"))
		
		# Create Sales Invoice
		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = customer
		invoice.posting_date = getdate(pinjaman_pencairan.approved_at) if pinjaman_pencairan.approved_at else nowdate()
		invoice.due_date = invoice.posting_date
		invoice.company = company
		
		# Set custom fields
		invoice.custom_pinjaman_id = pinjaman.name
		invoice.custom_pinjaman_pencairan_id = pinjaman_pencairan.name
		invoice.custom_invoice_type = "Disbursement"
		
		# Get Pinjaman Produk for admin fee
		produk = frappe.get_doc("Pinjaman Produk", pinjaman.pinjaman_produk_id)
		
		# Add disbursement item
		invoice.append("items", {
			"item_code": "LOAN-DISB",
			"item_name": f"Loan Disbursement - {pinjaman.name}",
			"description": f"Disbursement for loan {pinjaman.name}",
			"qty": 1,
			"rate": pinjaman_pencairan.nominal,
			"income_account": get_loans_receivable_account(company),
			"cost_center": get_default_cost_center(company)
		})
		
		# Add admin fee item (always show, even if 0)
		invoice.append("items", {
			"item_code": "LOAN-ADMIN-FEE",
			"item_name": f"Administration Fee - {pinjaman.name}",
			"description": f"Administration fee for loan {pinjaman.name}",
			"qty": 1,
			"rate": produk.admin_fee if produk.admin_fee else 0,
			"income_account": get_loan_income_account(company),
			"cost_center": get_default_cost_center(company)
		})
		
		# Insert only (don't submit) - will be submitted when Pinjaman Pencairan is approved
		invoice.insert(ignore_permissions=True)
		
		frappe.logger().info(f"Created disbursement invoice {invoice.name} (draft) for Pinjaman Pencairan {pinjaman_pencairan.name}")
		
		return invoice.name
		
	except Exception as e:
		frappe.log_error(f"Error creating disbursement invoice: {str(e)}", "Pinjaman Invoice Creation Error")
		frappe.throw(_("Failed to create disbursement invoice: {0}").format(str(e)))


def create_installment_invoices(pinjaman_id):
	"""
	Create Sales Invoices for all Pinjaman Installments
	
	Args:
		pinjaman_id (str): Pinjaman ID
		
	Returns:
		list: List of created invoice names
	"""
	try:
		# Get Pinjaman
		pinjaman = frappe.get_doc("Pinjaman", pinjaman_id)
		
		# Get or create customer
		customer = get_or_create_customer(pinjaman.profile_id)
		
		# Get default company
		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
		
		if not company:
			frappe.throw(_("Please set a default company"))
		
		# Get all installments for this Pinjaman
		installments = frappe.get_all(
			"Pinjaman Installment",
			filters={"pinjaman_id": pinjaman_id},
			fields=["name", "no", "due_date", "nominal_pokok", "nominal_bunga"],
			order_by="no asc"
		)
		
		created_invoices = []
		
		for inst_data in installments:
			# Get full installment document
			installment = frappe.get_doc("Pinjaman Installment", inst_data.name)
			
			# Skip if invoice already created
			if installment.installment_invoice:
				continue
			
			# Create Sales Invoice
			invoice = frappe.new_doc("Sales Invoice")
			invoice.customer = customer
			invoice.posting_date = nowdate()
			invoice.due_date = getdate(inst_data.due_date)
			invoice.company = company
			
			# Set custom fields
			invoice.custom_pinjaman_id = pinjaman_id
			invoice.custom_pinjaman_installment_id = inst_data.name
			invoice.custom_invoice_type = "Installment"
			invoice.custom_installment_number = inst_data.no
			
			# Add principal item (if > 0)
			if inst_data.nominal_pokok > 0:
				invoice.append("items", {
					"item_code": "LOAN-INST-PRINCIPAL",
					"item_name": f"Installment #{inst_data.no} - Principal",
					"description": f"Loan {pinjaman.name} - Installment #{inst_data.no} - Principal",
					"qty": 1,
					"rate": inst_data.nominal_pokok,
					"income_account": get_loans_receivable_account(company),
					"cost_center": get_default_cost_center(company)
				})
			
			# Add interest item (if > 0)
			if inst_data.nominal_bunga > 0:
				invoice.append("items", {
					"item_code": "LOAN-INST-INTEREST",
					"item_name": f"Installment #{inst_data.no} - Interest",
					"description": f"Loan {pinjaman.name} - Installment #{inst_data.no} - Interest",
					"qty": 1,
					"rate": inst_data.nominal_bunga,
					"income_account": get_loan_income_account(company),
					"cost_center": get_default_cost_center(company)
				})
			
			# Insert and submit
			invoice.insert(ignore_permissions=True)
			invoice.flags.ignore_permissions = True
			invoice.submit()
			
			# Update installment with invoice reference
			installment.installment_invoice = invoice.name
			installment.payment_status = "Unpaid"
			installment.save(ignore_permissions=True)
			
			created_invoices.append(invoice.name)
			
			frappe.logger().info(f"Created installment invoice {invoice.name} for Pinjaman Installment {inst_data.name}")
		
		return created_invoices
		
	except Exception as e:
		frappe.log_error(f"Error creating installment invoices: {str(e)}", "Pinjaman Invoice Creation Error")
		frappe.throw(_("Failed to create installment invoices: {0}").format(str(e)))


def get_loans_receivable_account(company):
	"""
	Get Loans Receivable account for the company
	
	Args:
		company (str): Company name
		
	Returns:
		str: Account name
	"""
	# Try to find existing Loans Receivable account
	account = frappe.db.get_value(
		"Account",
		{
			"account_name": "Loans Receivable",
			"company": company,
			"is_group": 0
		},
		"name"
	)
	
	if account:
		return account
	
	# If not found, try to create it
	return create_loans_receivable_account(company)


def get_loan_income_account(company):
	"""
	Get Loan Income account for the company
	
	Args:
		company (str): Company name
		
	Returns:
		str: Account name
	"""
	# Try to find existing Loan Income account
	account = frappe.db.get_value(
		"Account",
		{
			"account_name": "Loan Income",
			"company": company,
			"is_group": 0
		},
		"name"
	)
	
	if account:
		return account
	
	# If not found, try to create it
	return create_loan_income_account(company)


def create_loans_receivable_account(company):
	"""
	Create Loans Receivable account under Current Assets
	
	Args:
		company (str): Company name
		
	Returns:
		str: Account name
	"""
	# Find Current Assets parent account
	parent_account = frappe.db.get_value(
		"Account",
		{
			"account_name": "Current Assets",
			"company": company,
			"is_group": 1
		},
		"name"
	)
	
	if not parent_account:
		# Fallback to Application of Funds (Assets)
		parent_account = frappe.db.get_value(
			"Account",
			{
				"root_type": "Asset",
				"company": company,
				"is_group": 1
			},
			"name"
		)
	
	if not parent_account:
		frappe.throw(_("Cannot find parent account for Loans Receivable. Please create it manually."))
	
	# Create account
	account = frappe.new_doc("Account")
	account.account_name = "Loans Receivable"
	account.parent_account = parent_account
	account.company = company
	# Don't set account_type = "Receivable" as it requires customer linkage
	# This is a plain Asset account for tracking loans
	account.root_type = "Asset"
	account.is_group = 0
	account.insert(ignore_permissions=True)
	
	frappe.logger().info(f"Created Loans Receivable account for {company}")
	
	return account.name


def create_loan_income_account(company):
	"""
	Create Loan Income account under Income
	
	Args:
		company (str): Company name
		
	Returns:
		str: Account name
	"""
	# Find Income parent account
	parent_account = frappe.db.get_value(
		"Account",
		{
			"root_type": "Income",
			"company": company,
			"is_group": 1
		},
		"name"
	)
	
	if not parent_account:
		frappe.throw(_("Cannot find parent account for Loan Income. Please create it manually."))
	
	# Create account
	account = frappe.new_doc("Account")
	account.account_name = "Loan Income"
	account.parent_account = parent_account
	account.company = company
	account.root_type = "Income"
	account.is_group = 0
	account.insert(ignore_permissions=True)
	
	frappe.logger().info(f"Created Loan Income account for {company}")
	
	return account.name


def get_default_cost_center(company):
	"""
	Get default cost center for the company
	
	Args:
		company (str): Company name
		
	Returns:
		str: Cost Center name
	"""
	# Try to get default cost center from company
	cost_center = frappe.db.get_value("Company", company, "cost_center")
	
	if cost_center:
		return cost_center
	
	# Fallback: find any cost center for this company
	cost_center = frappe.db.get_value(
		"Cost Center",
		{"company": company, "is_group": 0},
		"name"
	)
	
	if cost_center:
		return cost_center
	

	frappe.throw(_("No cost center found for company {0}. Please set up a cost center.").format(company))



@frappe.whitelist(allow_guest=True)
def get_loan_invoices(flow_type=None):
	"""
	Get list of Sales Invoices related to loans (Disbursements and Installments).
	
	Args:
		flow_type (str, optional): 'Disbursement' or 'Installment'.
		
	Returns:
		list: List of invoice dicts with 'flow_type'.
	"""
	
	conditions = ""
	params = {}
	
	# Determine invoice types based on flow_type
	if flow_type:
		if flow_type.lower() in ["disbursement"]:
			conditions += " AND si.custom_invoice_type = 'Disbursement'"
		elif flow_type.lower() in ["installment"]:
			conditions += " AND si.custom_invoice_type = 'Installment'"
	
	query = f"""
		SELECT 
			si.name, si.posting_date, si.due_date, si.grand_total, si.status,
			si.custom_invoice_type, si.custom_pinjaman_id, si.custom_pinjaman_installment_id,
			p.profile_id,
			si.custom_invoice_type as flow_type
		FROM 
			`tabSales Invoice` si
		LEFT JOIN
			`tabPinjaman` p ON p.name = si.custom_pinjaman_id
		WHERE 
			si.custom_invoice_type IN ('Disbursement', 'Installment')
			AND si.docstatus = 1
			{conditions}
		ORDER BY 
			si.posting_date DESC, si.creation DESC
	"""
	
	data = frappe.db.sql(query, params, as_dict=True)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = data
