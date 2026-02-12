"""
Setup script for Pinjaman-ERPNext integration
Creates required master data: Items, Customer Group, and Accounts
"""
import frappe
from frappe import _


def setup_loan_master_data():
	"""
	Setup all required master data for loan integration
	"""
	print("Setting up Pinjaman-ERPNext integration master data...")
	
	# Create Items
	create_loan_items()
	
	# Create Customer Group
	create_customer_group()
	
	print("Master data setup completed successfully!")


def create_loan_items():
	"""
	Create loan-related service items
	"""
	items = [
		{
			"item_code": "LOAN-DISB",
			"item_name": "Loan Disbursement",
			"item_group": "Services",
			"stock_uom": "Nos",
			"is_stock_item": 0,
			"is_sales_item": 1,
			"is_service_item": 1,
			"description": "Loan disbursement service item"
		},
		{
			"item_code": "LOAN-ADMIN-FEE",
			"item_name": "Loan Administration Fee",
			"item_group": "Services",
			"stock_uom": "Nos",
			"is_stock_item": 0,
			"is_sales_item": 1,
			"is_service_item": 1,
			"description": "Loan administration fee"
		},
		{
			"item_code": "LOAN-INST-PRINCIPAL",
			"item_name": "Loan Installment - Principal",
			"item_group": "Services",
			"stock_uom": "Nos",
			"is_stock_item": 0,
			"is_sales_item": 1,
			"is_service_item": 1,
			"description": "Loan installment principal repayment"
		},
		{
			"item_code": "LOAN-INST-INTEREST",
			"item_name": "Loan Installment - Interest",
			"item_group": "Services",
			"stock_uom": "Nos",
			"is_stock_item": 0,
			"is_sales_item": 1,
			"is_service_item": 1,
			"description": "Loan installment interest payment"
		}
	]
	
	for item_data in items:
		if not frappe.db.exists("Item", item_data["item_code"]):
			item = frappe.new_doc("Item")
			item.update(item_data)
			item.insert(ignore_permissions=True)
			print(f"✓ Created item: {item_data['item_code']}")
		else:
			print(f"  Item already exists: {item_data['item_code']}")


def create_customer_group():
	"""
	Create Loan Borrowers customer group
	"""
	group_name = "Loan Borrowers"
	
	if not frappe.db.exists("Customer Group", group_name):
		customer_group = frappe.new_doc("Customer Group")
		customer_group.customer_group_name = group_name
		customer_group.parent_customer_group = "All Customer Groups"
		customer_group.is_group = 0
		customer_group.insert(ignore_permissions=True)
		print(f"✓ Created customer group: {group_name}")
	else:
		print(f"  Customer group already exists: {group_name}")


if __name__ == "__main__":
	setup_loan_master_data()
	frappe.db.commit()
