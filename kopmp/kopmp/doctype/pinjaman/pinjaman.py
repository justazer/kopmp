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

		# Send Email Notification
		email = frappe.db.get_value("User Profile", self.profile_id, "email")
		if email:
			subject = f"Pinjaman Created: {self.name}"
			message = f"Dear User,<br><br>Your Pinjaman application {self.name} for {self.nominal} has been created and is currently Requested.<br><br>Thank you."
			frappe.sendmail(recipients='reza.baharsyah@indocyber.id', subject=subject, message=message, sender='Koperasi App <no-reply@brevosend.com>' ,delayed=False)
