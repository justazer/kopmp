# Copyright (c) 2026, riski and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

class UserProfileKoperasi(WebsiteGenerator):
	def validate(self):
		self.sync_user_status()

	def sync_user_status(self):
		if not self.user:
			return

		user_doc = frappe.get_doc("User", self.user)
		
		# Map Member Status to User Enabled (1=Enabled, 0=Disabled)
		# Only 'Active' status enables the user. 'Pending' and 'Inactive' disable it.
		target_enabled = 1 if self.status == "Active" else 0
		
		if user_doc.enabled != target_enabled:
			user_doc.enabled = target_enabled
			user_doc.save(ignore_permissions=True)
			frappe.msgprint(f"User {self.user} status updated to {'Enabled' if target_enabled else 'Disabled'}")
