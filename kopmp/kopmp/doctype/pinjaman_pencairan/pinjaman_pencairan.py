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
		
		if produk.tipe == "Anuitas":
			# Placeholder for Anuitas logic
			pass
		else:
			# Ensure fields are floats for calculation
			nominal = float(pinjaman.nominal)
			rate_percent = float(pinjaman.rate)
			top = int(pinjaman.top)
			
			nominal_pokok = nominal / top
			nominal_bunga = nominal * (rate_percent / 100)
			
			# Start next month
			start_date = getdate(self.approved_at) or getdate()
			# Logic: 1st of next month
			next_month = start_date + relativedelta(months=1)
			first_due_date = get_first_day(next_month)
			
			current_due_date = getdate(first_due_date)

			for i in range(1, top + 1):
				doc = frappe.new_doc("Pinjaman Installment")
				doc.pinjaman_id = self.pinjaman_id
				doc.no = i
				doc.due_date = current_due_date
				doc.nominal_pokok = nominal_pokok
				doc.nominal_bunga = nominal_bunga
				# doc.amount and doc.status do not exist in the DocType
				# Status is inferred from paid_date (if set, it's paid)
				doc.insert()
				
				# Increment month
				current_due_date = current_due_date + relativedelta(months=1)
