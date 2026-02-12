"""
Payment tracking utilities for Pinjaman integration
"""
import frappe
from frappe import _


def update_installment_payment_status(payment_entry, method):
	"""
	Update Pinjaman Installment payment status when Payment Entry is submitted
	
	Args:
		payment_entry: Payment Entry document
		method: Event method (on_submit)
	"""
	try:
		# Loop through payment references
		for ref in payment_entry.references:
			# Check if reference is a Sales Invoice
			if ref.reference_doctype == "Sales Invoice":
				# Get the invoice
				invoice = frappe.get_doc("Sales Invoice", ref.reference_name)
				
				# Check if this invoice is linked to a Pinjaman Installment
				if hasattr(invoice, 'custom_pinjaman_installment_id') and invoice.custom_pinjaman_installment_id:
					update_installment_status(
						invoice.custom_pinjaman_installment_id,
						payment_entry.name,
						payment_entry.posting_date,
						ref.allocated_amount,
						invoice.outstanding_amount
					)
	
	except Exception as e:
		frappe.log_error(f"Error updating installment payment status: {str(e)}", "Payment Status Update Error")
		# Don't throw error to avoid blocking payment entry submission


def cancel_installment_payment(payment_entry, method):
	"""
	Revert Pinjaman Installment payment status when Payment Entry is cancelled
	
	Args:
		payment_entry: Payment Entry document
		method: Event method (on_cancel)
	"""
	try:
		# Loop through payment references
		for ref in payment_entry.references:
			# Check if reference is a Sales Invoice
			if ref.reference_doctype == "Sales Invoice":
				# Get the invoice
				invoice = frappe.get_doc("Sales Invoice", ref.reference_name)
				
				# Check if this invoice is linked to a Pinjaman Installment
				if hasattr(invoice, 'custom_pinjaman_installment_id') and invoice.custom_pinjaman_installment_id:
					# Get installment
					installment = frappe.get_doc("Pinjaman Installment", invoice.custom_pinjaman_installment_id)
					
					# Reset payment fields if this was the payment entry
					if installment.payment_entry == payment_entry.name:
						installment.payment_entry = None
						installment.paid_date = None
						installment.paid_pokok = 0
						installment.paid_bunga = 0
						
						# Update status based on invoice outstanding
						if invoice.outstanding_amount == invoice.grand_total:
							installment.payment_status = "Unpaid"
						elif invoice.outstanding_amount > 0:
							installment.payment_status = "Partial"
						else:
							installment.payment_status = "Paid"
						
						installment.save(ignore_permissions=True)
						
						frappe.logger().info(f"Reverted payment status for Pinjaman Installment {installment.name}")
	
	except Exception as e:
		frappe.log_error(f"Error reverting installment payment status: {str(e)}", "Payment Status Update Error")
		# Don't throw error to avoid blocking payment entry cancellation


def update_installment_status(installment_id, payment_entry_name, payment_date, allocated_amount, outstanding_amount):
	"""
	Update Pinjaman Installment with payment details
	
	Args:
		installment_id (str): Pinjaman Installment ID
		payment_entry_name (str): Payment Entry name
		payment_date (date): Payment date
		allocated_amount (float): Amount allocated in this payment
		outstanding_amount (float): Remaining outstanding amount on invoice
	"""
	installment = frappe.get_doc("Pinjaman Installment", installment_id)
	
	# Update payment entry reference
	installment.payment_entry = payment_entry_name
	
	# Update paid date
	installment.paid_date = payment_date
	
	# Update paid amounts
	# Note: We're storing the allocated amount in paid_pokok for simplicity
	# In a more complex scenario, you might want to split between pokok and bunga
	installment.paid_pokok = allocated_amount
	
	# Update payment status based on outstanding amount
	if outstanding_amount == 0:
		installment.payment_status = "Paid"
	elif outstanding_amount > 0 and allocated_amount > 0:
		installment.payment_status = "Partial"
	else:
		installment.payment_status = "Unpaid"
	
	# Save installment
	installment.save(ignore_permissions=True)
	
	frappe.logger().info(
		f"Updated Pinjaman Installment {installment_id}: "
		f"Status={installment.payment_status}, "
		f"Paid={allocated_amount}, "
		f"Outstanding={outstanding_amount}"
	)
