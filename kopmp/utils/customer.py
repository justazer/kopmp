"""
Customer management utilities for Pinjaman integration
"""
import frappe
from frappe import _


def get_or_create_customer(profile_id):
	"""
	Get or create Customer from User Profile
	
	Args:
		profile_id (str): User Profile ID
		
	Returns:
		str: Customer name
	"""
	if not profile_id:
		frappe.throw(_("Profile ID is required"))
	
	# Customer naming: CUST-{profile_id}
	customer_name = f"CUST-{profile_id}"
	
	# Check if customer already exists
	if frappe.db.exists("Customer", customer_name):
		return customer_name
	
	# Get User Profile details
	user_profile = frappe.get_doc("User Profile", profile_id)
	
	# Create new customer
	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_type = "Individual"
	
	# Set customer group (create if doesn't exist)
	customer_group = get_or_create_customer_group()
	customer.customer_group = customer_group
	
	# Set territory (use default or All Territories)
	customer.territory = frappe.db.get_single_value("Selling Settings", "territory") or "All Territories"
	
	# Link back to User Profile via custom field (if exists)
	if hasattr(customer, 'custom_user_profile_id'):
		customer.custom_user_profile_id = profile_id
	
	# Get email from User Profile if available
	if hasattr(user_profile, 'email') and user_profile.email:
		customer.email_id = user_profile.email
	
	# Get phone from User Profile if available
	if hasattr(user_profile, 'phone') and user_profile.phone:
		customer.mobile_no = user_profile.phone
	
	# Insert customer
	customer.insert(ignore_permissions=True)
	
	frappe.logger().info(f"Created customer {customer_name} for User Profile {profile_id}")
	
	return customer.name


def get_or_create_customer_group():
	"""
	Get or create 'Loan Borrowers' customer group
	
	Returns:
		str: Customer Group name
	"""
	group_name = "Loan Borrowers"
	
	if frappe.db.exists("Customer Group", group_name):
		return group_name
	
	# Create customer group
	customer_group = frappe.new_doc("Customer Group")
	customer_group.customer_group_name = group_name
	customer_group.parent_customer_group = "All Customer Groups"
	customer_group.is_group = 0
	customer_group.insert(ignore_permissions=True)
	
	frappe.logger().info(f"Created customer group: {group_name}")
	
	return customer_group.name
