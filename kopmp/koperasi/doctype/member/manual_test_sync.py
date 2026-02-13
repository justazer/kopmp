import frappe
from koperasi.koperasi.doctype.member.member import Member

def test_sync():
    # 1. Create a Test User
    user_email = "test_member_sync@example.com"
    if frappe.db.exists("User", user_email):
        frappe.delete_doc("User", user_email)
    
    user = frappe.get_doc({
        "doctype": "User",
        "email": user_email,
        "first_name": "Test",
        "enabled": 1,
        "send_welcome_email": 0
    }).insert(ignore_permissions=True)
    
    print(f"Created User: {user.name}, Enabled: {user.enabled}")

    # 2. Create a Member linked to User
    if frappe.db.exists("Member", {"user": user_email}):
        frappe.delete_doc("Member", {"user": user_email})

    member = frappe.get_doc({
        "doctype": "Member",
        "user": user_email,
        "full_name": "Test Member",
        "status": "Active" # Should keep user enabled
    }).insert(ignore_permissions=True)
    
    print(f"Created Member: {member.name}, Status: {member.status}")

    # Verify initial state
    user.reload()
    assert user.enabled == 1, "User should be enabled initially"
    print("Initial state verification PASSED")

    # 3. Update Member to Inactive
    member.status = "Inactive"
    member.save(ignore_permissions=True)
    print(f"Updated Member Status to: {member.status}")

    # Verify User is disabled
    user.reload()
    print(f"User Enabled status: {user.enabled}")
    assert user.enabled == 0, "User should be disabled when Member is Inactive"
    print("Inactive Sync Verification PASSED")

    # 4. Update Member to Active
    member.status = "Active"
    member.save(ignore_permissions=True)
    print(f"Updated Member Status to: {member.status}")

    # Verify User is enabled
    user.reload()
    print(f"User Enabled status: {user.enabled}")
    assert user.enabled == 1, "User should be enabled when Member is Active"
    print("Active Sync Verification PASSED")
    
    # Clean up
    frappe.delete_doc("Member", member.name)
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

