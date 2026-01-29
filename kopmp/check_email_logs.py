import frappe

def execute():
    print("--- recent Error Logs ---")
    errors = frappe.get_all("Error Log", fields=["method", "error", "creation"], order_by="creation desc", limit=5)
    for e in errors:
        print(f"[{e.creation}] {e.method}: {e.error}")

    print("\n--- Recent Email Queue ---")
    queue = frappe.get_all("Email Queue", fields=["name", "status", "error", "message", "creation"], order_by="creation desc", limit=5)
    for q in queue:
        print(f"[{q.creation}] {q.name} ({q.status}): {q.error}")
