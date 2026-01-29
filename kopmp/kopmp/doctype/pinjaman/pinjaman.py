# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Pinjaman(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.id = make_autoname("PJN-.#####")

	def after_insert(self):
		pencairan = frappe.new_doc("Pinjaman Pencairan")
		pencairan.pinjaman_id = self.name
		pencairan.nominal = self.nominal
		pencairan.status = "Requested"
		pencairan.request_at = self.request_at
		pencairan.approved_at = None
		pencairan.insert()
