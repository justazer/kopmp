import frappe
from frappe.model.document import Document
from frappe.utils import flt

class rat_user_pencairan(Document):
	def validate(self):
		# Determine parent rat_user
		rat_user_name = self.rat_user_id
		# Use .get() to avoid AttributeError if parent is not set
		if not rat_user_name and self.get("parent") and self.get("parenttype") == 'rat_user':
			rat_user_name = self.get("parent")

		if rat_user_name:
			# Get limit from rat_user
			shu_terbagi = frappe.db.get_value("rat_user", rat_user_name, "shu_terbagi") or 0
			
			total_pencairan = 0
			
			if self.get("parent") and self.get("parenttype") == 'rat_user':
				# It is being saved as a child table
				existing = frappe.db.sql("""
					SELECT SUM(nominal) FROM `tabrat_user_pencairan`
					WHERE parent = %s AND name != %s
				""", (rat_user_name, self.name))
				total_pencairan = flt(existing[0][0]) if existing else 0
			else:
				# It is being saved as a standalone doc linked via rat_user_id
				existing = frappe.db.sql("""
					SELECT SUM(nominal) FROM `tabrat_user_pencairan`
					WHERE rat_user_id = %s AND name != %s
				""", (rat_user_name, self.name))
				total_pencairan = flt(existing[0][0]) if existing else 0

			current_total = total_pencairan + flt(self.nominal)
			
			if current_total > flt(shu_terbagi):
				frappe.throw(f"Total pencairan ({current_total:,.2f}) exceeds SHU Terbagi ({shu_terbagi:,.2f}) for this user.")