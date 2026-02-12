"""
Clean up script for Pinjaman test data
Deletes: Pinjaman, Pinjaman Pencairan, Pinjaman Installment, and related Sales Invoices
Keeps: Pinjaman Produk, Pinjaman Produk TOP
"""
import frappe

def clean_pinjaman_data():
    """Delete all Pinjaman-related data except Pinjaman Produk"""
    print("🧹 Starting cleanup of Pinjaman data...")
    
    try:
        # Step 0: Clear link fields to avoid constraint errors
        print("\n0. Clearing link fields...")
        
        # Clear installment_invoice links in Pinjaman Installment
        frappe.db.sql("""
            UPDATE `tabPinjaman Installment` 
            SET installment_invoice = NULL, payment_entry = NULL
        """)
        
        # Clear disbursement_invoice link in Pinjaman Pencairan
        frappe.db.sql("""
            UPDATE `tabPinjaman Pencairan` 
            SET disbursement_invoice = NULL
        """)
        
        frappe.db.commit()
        print("   ✓ Link fields cleared")
        
        # Step 0.5: Delete Payment Ledger Entries and GL Entries for Pinjaman invoices
        print("\n0.5. Deleting Payment Ledger Entries and GL Entries...")
        
        # Get all Pinjaman-related invoices
        invoice_names = frappe.db.sql_list("""
            SELECT name FROM `tabSales Invoice`
            WHERE custom_pinjaman_id IS NOT NULL AND custom_pinjaman_id != ''
        """)
        
        if invoice_names:
            # Delete Payment Ledger Entries
            frappe.db.sql("""
                DELETE FROM `tabPayment Ledger Entry`
                WHERE voucher_type = 'Sales Invoice' 
                AND voucher_no IN ({})
            """.format(','.join(['%s'] * len(invoice_names))), invoice_names)
            
            # Delete GL Entries
            frappe.db.sql("""
                DELETE FROM `tabGL Entry`
                WHERE voucher_type = 'Sales Invoice' 
                AND voucher_no IN ({})
            """.format(','.join(['%s'] * len(invoice_names))), invoice_names)
            
            frappe.db.commit()
            print(f"   ✓ Deleted ledger entries for {len(invoice_names)} invoices")
        
        # 1. Delete Sales Invoices linked to Pinjaman
        print("\n1. Deleting Sales Invoices linked to Pinjaman...")
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=[
                ["custom_pinjaman_id", "!=", ""]
            ],
            fields=["name", "docstatus"]
        )
        
        for inv in invoices:
            try:
                doc = frappe.get_doc("Sales Invoice", inv.name)
                if doc.docstatus == 1:  # Submitted
                    doc.cancel()
                    print(f"   Cancelled: {inv.name}")
                doc.delete()
                print(f"   ✓ Deleted: {inv.name}")
            except Exception as e:
                print(f"   ✗ Error deleting {inv.name}: {str(e)}")
        
        print(f"   Total invoices deleted: {len(invoices)}")
        

        # 2. Delete Pinjaman Installments
        print("\n2. Deleting Pinjaman Installments...")
        installments = frappe.get_all("Pinjaman Installment", fields=["name", "docstatus"])
        
        for inst in installments:
            try:
                if inst.docstatus == 1:
                    doc = frappe.get_doc("Pinjaman Installment", inst.name)
                    doc.cancel()
                    print(f"   Cancelled: {inst.name}")
                    
                frappe.delete_doc("Pinjaman Installment", inst.name, force=1)
            except Exception as e:
                print(f"   ✗ Error deleting {inst.name}: {str(e)}")
                # Try direct SQL delete if standard way fails (Desperate cleanup)
                try:
                    frappe.db.sql("DELETE FROM `tabPinjaman Installment` WHERE name=%s", inst.name)
                    print(f"   ✓ Force deleted via SQL: {inst.name}")
                except Exception as sql_e:
                    print(f"   ✗ SQL Delete failed: {str(sql_e)}")
        
        print(f"   ✓ Deleted {len(installments)} installments")
        
        # 3. Delete Pinjaman Pencairan
        print("\n3. Deleting Pinjaman Pencairan...")
        pencairans = frappe.get_all("Pinjaman Pencairan", fields=["name", "docstatus"])
        
        for pen in pencairans:
            try:
                doc = frappe.get_doc("Pinjaman Pencairan", pen.name)
                if doc.docstatus == 1:  # Submitted
                    doc.cancel()
                    print(f"   Cancelled: {pen.name}")
                doc.delete()
            except Exception as e:
                print(f"   ✗ Error deleting {pen.name}: {str(e)}")
        
        print(f"   ✓ Deleted {len(pencairans)} pencairans")
        
        # 4. Delete Pinjaman
        print("\n4. Deleting Pinjaman...")
        pinjamans = frappe.get_all("Pinjaman", fields=["name", "docstatus"])
        
        for pjn in pinjamans:
            try:
                doc = frappe.get_doc("Pinjaman", pjn.name)
                if doc.docstatus == 1:  # Submitted
                    doc.cancel()
                    print(f"   Cancelled: {pjn.name}")
                doc.delete()
            except Exception as e:
                print(f"   ✗ Error deleting {pjn.name}: {str(e)}")
        
        print(f"   ✓ Deleted {len(pinjamans)} pinjamans")
        
        # Commit changes
        frappe.db.commit()
        
        print("\n✅ Cleanup completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Sales Invoices: {len(invoices)} deleted")
        print(f"   - Pinjaman Installments: {len(installments)} deleted")
        print(f"   - Pinjaman Pencairan: {len(pencairans)} deleted")
        print(f"   - Pinjaman: {len(pinjamans)} deleted")
        print("\n✓ Pinjaman Produk and Pinjaman Produk TOP were NOT deleted (kept intact)")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_pinjaman_data()

