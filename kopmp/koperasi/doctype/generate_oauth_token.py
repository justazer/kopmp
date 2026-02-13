import frappe
from frappe.oauth import create_oauth2_client
from datetime import timedelta

def generate_test_token():
    user = "demo@koperasi.com"
    app_name = "Koperasi Mobile App"
    
    # 1. Create/Get OAuth Client
    client_id = frappe.db.get_value("OAuth Client", {"app_name": app_name}, "client_id")
    if not client_id:
        client = frappe.new_doc("OAuth Client")
        client.app_name = app_name
        client.user = user
        client.scopes = "all openid"
        client.redirect_uris = "http://localhost:8000/api/method/frappe.integrations.oauth2.approve"
        client.default_redirect_uri = "http://localhost:8000/api/method/frappe.integrations.oauth2.approve"
        client.save(ignore_permissions=True)
        frappe.db.commit()
        client_id = client.client_id
        print(f"Created OAuth Client: {client_id}")
    else:
        print(f"Using existing OAuth Client: {client_id}")

    # 2. Generate Bearer Token
    # We can manually create the doc since standard flow requires request object
    token = frappe.new_doc("OAuth Bearer Token")
    token.client = client_id
    token.user = user
    token.scopes = "all openid"
    token.expires_in = 36000 # 10 hours
    token.refresh_token = frappe.generate_hash(length=30)
    token.access_token = frappe.generate_hash(length=30)
    token.save(ignore_permissions=True)
    frappe.db.commit()
    
    print("-" * 20)
    print(f"Access Token: {token.access_token}")
    print("-" * 20)
    print("Use this token in your header:")
    print(f"'Authorization': 'Bearer {token.access_token}'")

if __name__ == "__main__":
    generate_test_token()
