# Copyright (c) 2026, Administrator and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PinjamanInstallment(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.id = make_autoname("PJI-.#####")
