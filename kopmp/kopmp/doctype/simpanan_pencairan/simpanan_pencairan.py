import frappe
from frappe.model.document import Document


class SimpananPencairan(Document):
	pass


@frappe.whitelist(allow_guest=True)
def get_detail(profile_id):
	"""
	Get list of Simpanan Pencairan for a user profile.
	
	Args:
		profile_id (str): User Profile ID
		
	Returns:
		list: Simpanan Pencairan records with linked Simpanan Wajib info
	"""
	sw_ids = frappe.get_all("Simpanan Wajib", filters={"profile_id": profile_id}, pluck="name")
	
	if not sw_ids:
		frappe.response["message"] = "not_found"
		frappe.response["data"] = None
		return
	
	data = frappe.get_all(
		"Simpanan Pencairan",
		filters={"simpanan_wajib_id": ["in", sw_ids]},
		fields=["name", "simpanan_wajib_id", "nominal", "status", "request_at", "approved_at"],
		order_by="creation desc"
	)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = data


@frappe.whitelist(allow_guest=True)
def get_list():
	"""
	Get list of all Simpanan Pencairan.
	
	Returns:
		list: All Simpanan Pencairan records
	"""
	data = frappe.get_all(
		"Simpanan Pencairan",
		fields=["name", "simpanan_wajib_id", "nominal", "status", "request_at", "approved_at"],
		order_by="creation desc"
	)
	
	frappe.response["message"] = "success"
	frappe.response["data"] = data


@frappe.whitelist(allow_guest=True)
def approve_pencairan(pencairan_id, action):
	"""
	Approve or reject a Simpanan Pencairan.
	
	Args:
		pencairan_id (str): Simpanan Pencairan ID
		action (str): 'approve' or 'reject'
	"""
	if action not in ("approve", "reject"):
		frappe.throw("Action harus 'approve' atau 'reject'")
	
	original_user = frappe.session.user
	frappe.set_user("Administrator")
	
	try:
		return _process_approval(pencairan_id, action)
	finally:
		frappe.set_user(original_user)


def _process_approval(pencairan_id, action):
	from frappe.utils import nowdate
	
	pencairan = frappe.get_doc("Simpanan Pencairan", pencairan_id)
	
	if pencairan.status != "Pending":
		frappe.throw(f"Pencairan {pencairan_id} sudah di-{pencairan.status.lower()}")
	
	if action == "reject":
		pencairan.status = "Rejected"
		pencairan.save(ignore_permissions=True)
		frappe.db.commit()
		
		frappe.response["message"] = "success"
		frappe.response["data"] = {
			"pencairan_id": pencairan_id,
			"status": "Rejected"
		}
		return
	
	# Approve flow
	simpanan_wajib = frappe.get_doc("Simpanan Wajib", pencairan.simpanan_wajib_id)
	saldo_awal = simpanan_wajib.saldo or 0
	
	if saldo_awal < pencairan.nominal:
		frappe.throw(f"Saldo tidak mencukupi. Saldo: {saldo_awal}, Nominal pencairan: {pencairan.nominal}")
	
	saldo_akhir = saldo_awal - pencairan.nominal
	
	# Create Simpanan Wajib Log (withdrawal)
	log = frappe.new_doc("Simpanan Wajib Log")
	log.simpanan_wajib_id = pencairan.simpanan_wajib_id
	log.nominal = -pencairan.nominal
	log.saldo_awal = saldo_awal
	log.saldo_akhir = saldo_akhir
	log.insert(ignore_permissions=True)
	
	# Update saldo
	simpanan_wajib.saldo = saldo_akhir
	simpanan_wajib.save(ignore_permissions=True)
	
	# Update pencairan status
	pencairan.status = "Approved"
	pencairan.approved_at = nowdate()
	pencairan.save(ignore_permissions=True)
	
	frappe.db.commit()
	
	frappe.response["message"] = "success"
	frappe.response["data"] = {
		"pencairan_id": pencairan_id,
		"status": "Approved",
		"nominal": pencairan.nominal,
		"saldo_awal": saldo_awal,
		"saldo_akhir": saldo_akhir,
		"log_id": log.name
	}
