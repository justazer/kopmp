# Copyright (c) 2026, . and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document


class rat_user(Document):
    def validate(self):
        total_pencairan = 0
        for row in self.pencairan:
            total_pencairan += flt(row.nominal)
        
        if total_pencairan > flt(self.shu_terbagi):
            frappe.throw(f"Total pencairan ({total_pencairan:,.2f}) melebihi SHU Terbagi ({flt(self.shu_terbagi):,.2f})")

    @frappe.whitelist()
    def generate_token_rat(self):
        """
        Generates a token for the user.
        """
        import hashlib
        token = hashlib.sha256((self.name + self.user_id).encode()).hexdigest()
        return token

    @frappe.whitelist()
    def approve_with_token(self, token_user):
        """
        Approves the document if the token is valid.
        """
        import hashlib
        expected_token = hashlib.sha256((self.name + self.user_id).encode()).hexdigest()
        
        if token_user.strip() == expected_token:
            self.approved_at = frappe.utils.now_datetime()
            self.approved_sign = self.user_id
            self.save()
            frappe.db.commit()
            return "Approved successfully"
        else:
            frappe.throw("Invalid Token")


@frappe.whitelist(allow_guest=False)
def approve_rat_user_by_token(token_user):
    """
    Standalone API method to approve a rat_user by token only.
    No need to pass document name — finds the matching rat_user automatically.
    """
    import hashlib

    if not token_user:
        frappe.throw("Token is required")

    token_user = token_user.strip()

    # Get all rat_user documents that are not yet approved
    rat_users = frappe.get_all("rat_user", filters={"approved_at": ["is", "not set"]}, fields=["name", "user_id"])

    for ru in rat_users:
        expected_token = hashlib.sha256((ru.name + ru.user_id).encode()).hexdigest()
        if token_user == expected_token:
            doc = frappe.get_doc("rat_user", ru.name)
            doc.approved_at = frappe.utils.now_datetime()
            doc.approved_sign = doc.user_id
            doc.save()
            frappe.db.commit()
            return {"message": "Approved successfully", "rat_user": doc.name, "user_id": doc.user_id}

    frappe.throw("Invalid Token or user already approved")