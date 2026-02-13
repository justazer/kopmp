import frappe
from koperasi.koperasi.doctype.user_profile_koperasi.user_profile_koperasi import UserProfileKoperasi

def test_sync():
    # 1. Create a Test User
    user_email = "test_upk_sync@example.com"
    if frappe.db.exists("User", user_email):
        frappe.delete_doc("User", user_email)
    
    user = frappe.get_doc({
        "doctype": "User",
        "email": user_email,
        "first_name": "Test UPK",
        "enabled": 1,
        "send_welcome_email": 0
    }).insert(ignore_permissions=True)
    
    print(f"Created User: {user.name}, Enabled: {user.enabled}")

    # 2. Create a User Profile Koperasi linked to User
    if frappe.db.exists("User Profile Koperasi", {"user": user_email}):
        # Need to allow delete if linked
        upk_name = frappe.db.get_value("User Profile Koperasi", {"user": user_email})
        frappe.delete_doc("User Profile Koperasi", upk_name)

    upk = frappe.get_doc({
        "doctype": "User Profile Koperasi",
        "user": user_email,
        "full_name": "Test Member UPK",
        "status": "Active" # Should keep user enabled
    }).insert(ignore_permissions=True)
    
    print(f"Created UPK: {upk.name}, Status: {upk.status}")

    # Verify initial state
    user.reload()
    assert user.enabled == 1, "User should be enabled initially"
    print("Initial state verification PASSED")

    # 3. Update UPK to Inactive
    upk.status = "Inactive"
    upk.save(ignore_permissions=True)
    print(f"Updated UPK Status to: {upk.status}")

    # Verify User is disabled
    user.reload()
    print(f"User Enabled status: {user.enabled}")
    assert user.enabled == 0, "User should be disabled when UPK is Inactive"
    print("Inactive Sync Verification PASSED")

    # 4. Update UPK to Pending
    upk.status = "Pending"
    upk.save(ignore_permissions=True)
    print(f"Updated UPK Status to: {upk.status}")
    
    # Verify User is disabled (Pending should also disable?)
    # My logic: target_enabled = 1 if self.status == "Active" else 0
    # So Pending -> Disabled.
    user.reload()
    print(f"User Enabled status: {user.enabled}")
    assert user.enabled == 0, "User should be disabled when UPK is Pending"
    print("Pending Sync Verification PASSED")

    # 5. Update UPK to Active
    upk.status = "Active"
    upk.save(ignore_permissions=True)
    print(f"Updated UPK Status to: {upk.status}")

    # Verify User is enabled
    user.reload()
    print(f"User Enabled status: {user.enabled}")
    assert user.enabled == 1, "User should be enabled when UPK is Active"
    print("Active Sync Verification PASSED")
    
    # Clean up
    frappe.delete_doc("User Profile Koperasi", upk.name)
    frappe.delete_doc("User", user.name)
    print("Cleanup done.")

if __name__ == "__main__":
    try:
        test_sync()
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
