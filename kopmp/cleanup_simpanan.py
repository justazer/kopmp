import frappe

def cleanup():
    print("=== Cleaning up Simpanan data ===")

    # 1. Delete Simpanan Pokok Tagihan
    tagihan_sp = frappe.get_all("Simpanan Pokok Tagihan")
    for t in tagihan_sp:
        print(f"  Deleting Simpanan Pokok Tagihan: {t.name}")
        frappe.delete_doc("Simpanan Pokok Tagihan", t.name, force=1)

    # 2. Delete Simpanan Wajib Tagihan
    tagihan_sw = frappe.get_all("Simpanan Wajib Tagihan")
    for t in tagihan_sw:
        print(f"  Deleting Simpanan Wajib Tagihan: {t.name}")
        frappe.delete_doc("Simpanan Wajib Tagihan", t.name, force=1)

    # 3. Delete related Sales Invoices (Simpanan Pokok + Simpanan Wajib)
    invoices = frappe.db.sql("""
        SELECT name FROM `tabSales Invoice`
        WHERE (custom_simpanan_pokok_id IS NOT NULL AND custom_simpanan_pokok_id != '')
           OR (custom_simpanan_wajib_id IS NOT NULL AND custom_simpanan_wajib_id != '')
    """, as_dict=True)

    for inv in invoices:
        print(f"  Processing Sales Invoice: {inv.name}")
        try:
            # Delete Payment Ledger Entries
            ples = frappe.get_all("Payment Ledger Entry", filters={"voucher_type": "Sales Invoice", "voucher_no": inv.name})
            for ple in ples:
                print(f"    Deleting Payment Ledger Entry: {ple.name}")
                frappe.delete_doc("Payment Ledger Entry", ple.name, force=1)

            # Delete GL Entries
            gles = frappe.get_all("GL Entry", filters={"voucher_type": "Sales Invoice", "voucher_no": inv.name})
            for gle in gles:
                print(f"    Deleting GL Entry: {gle.name}")
                frappe.delete_doc("GL Entry", gle.name, force=1)

            # Cancel if submitted, then delete
            doc = frappe.get_doc("Sales Invoice", inv.name)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc("Sales Invoice", inv.name, force=1)
            print(f"  Deleted Sales Invoice: {inv.name}")
        except Exception as e:
            print(f"    Error: {e}")

    # 4. Delete Simpanan Pokok
    sp_list = frappe.get_all("Simpanan Pokok")
    for sp in sp_list:
        print(f"  Deleting Simpanan Pokok: {sp.name}")
        frappe.delete_doc("Simpanan Pokok", sp.name, force=1)

    # 5. Delete Simpanan Wajib
    sw_list = frappe.get_all("Simpanan Wajib")
    for sw in sw_list:
        print(f"  Deleting Simpanan Wajib: {sw.name}")
        frappe.delete_doc("Simpanan Wajib", sw.name, force=1)

    frappe.db.commit()
    print("=== Cleanup completed ===")
