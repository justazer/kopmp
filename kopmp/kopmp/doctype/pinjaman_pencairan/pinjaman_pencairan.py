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
			self.create_installments()

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
				doc.nominal_pokok = principal_payment + monthly_admin_fee
				doc.nominal_bunga = interest_payment
				doc.insert()
				
				current_due_date = current_due_date + relativedelta(months=1)

		else:
			# --- Standard Flat Logic ---
			# Nominal Pokok includes Principal + Admin Fee (Monthly)
			nominal_pokok = (nominal / top) + admin_fee
			nominal_bunga = nominal * (rate_percent / 100)

			for i in range(1, top + 1):
				doc = frappe.new_doc("Pinjaman Installment")
				doc.pinjaman_id = self.pinjaman_id
				doc.no = i
				doc.due_date = current_due_date
				doc.nominal_pokok = nominal_pokok
				doc.nominal_bunga = nominal_bunga
				doc.insert()
				
				current_due_date = current_due_date + relativedelta(months=1)
