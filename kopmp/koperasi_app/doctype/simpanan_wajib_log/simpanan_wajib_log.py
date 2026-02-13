# Copyright (c) 2026, . and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class simpanan_wajib_log(Document):
    def after_insert(self):
        if self.simpanan_wajib_id:
            doc = frappe.get_doc("simpanan_wajib", self.simpanan_wajib_id)
            doc.saldo = self.saldo_akhir
            doc.save(ignore_permissions=True)
