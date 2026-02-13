# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document

class Member(Document):
	def validate(self):
		self.sync_user_status()

	def sync_user_status(self):
		if not self.user:
			return

		user_doc = frappe.get_doc("User", self.user)
		
		# Map Member Status to User Enabled (1=Enabled, 0=Disabled)
		target_enabled = 1 if self.status == "Active" else 0
		
		if user_doc.enabled != target_enabled:
			user_doc.enabled = target_enabled
			user_doc.save(ignore_permissions=True)
			frappe.msgprint(f"User {self.user} status updated to {'Enabled' if target_enabled else 'Disabled'}")
