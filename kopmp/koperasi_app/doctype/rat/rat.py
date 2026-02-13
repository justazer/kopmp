# Copyright (c) 2026, . and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


@frappe.whitelist()
def create_rat(tahun, summary, date, shu_bersih, laba_ditahan):
	shu_bersih = float(shu_bersih)
	laba_ditahan = float(laba_ditahan)
	shu_terbagi = shu_bersih - laba_ditahan
	
	doc = frappe.new_doc("rat")
	doc.tahun = tahun
	doc.summary = summary
	doc.date = date
	doc.shu_bersih = shu_bersih
	doc.laba_ditahan = laba_ditahan
	doc.shu_terbagi = shu_terbagi
	doc.status = "Draft" # Default status
	doc.insert()
	
	return {
		"status": "success",
		"data": {
			"name": doc.name,
			"shu_terbagi": shu_terbagi
		}
	}


class rat(Document):
	@frappe.whitelist()
	def hitung_shu_anggota(self):
		# Get Global Data
		globals_data = self.get_user_financial_data(None)
		
		total_saldo_simpanan_wajib = globals_data.get('total_saldo_simpanan_wajib', 0)
		total_saldo_simpanan_pokok = globals_data.get('total_saldo_simpanan_pokok', 0)
		total_nominal_pinjaman = globals_data.get('total_nominal_pinjaman', 0)
		rat_users = globals_data.get('rat_users', [])
		
		results = []
		
		for member in rat_users:
			# Get User Financials & Calculations
			user_data = self.get_user_financial_data(member.user_id, globals_data)
			
			jasa_modal = user_data.get('jasa_modal', 0)
			jasa_usaha = user_data.get('jasa_usaha', 0)
			
			# if not hasattr(self, '_all_members_approved'):
			# 	unapproved = frappe.db.sql("""
			# 		SELECT name FROM `tabrat_user`
			# 		WHERE rat_id = %s AND (approved_at IS NULL OR approved_sign IS NULL OR approved_sign = '')
			# 		LIMIT 1
			# 	""", (self.name,))
			# 	self._all_members_approved = not unapproved
			# 	if unapproved:
			# 		frappe.msgprint("Warning: One or more members are not approved. SHU Terbagi will not be assigned.")

			# if self._all_members_approved:
			frappe.db.set_value("rat_user", member.name, "shu_terbagi", jasa_modal + jasa_usaha)
			
			results.append({
				"jasa_modal": jasa_modal,
				"jasa_usaha": jasa_usaha,
				"rat_user": member.name,
				"user_id": member.user_id,
				"simpanan_wajib": user_data.get('simpanan_wajib', 0),
				"simpanan_pokok": user_data.get('simpanan_pokok', 0),
				"pinjaman": user_data.get('pinjaman', 0),
				"total_saldo_simpanan_wajib_All": total_saldo_simpanan_wajib,
				"total_saldo_simpanan_pokok_All": total_saldo_simpanan_pokok,
				"total_nominal_pinjaman_All": total_nominal_pinjaman
			})
			
		return results

	@frappe.whitelist()
	def create_rat_users(self):
		active_users = frappe.get_all("user_profile", filters={"status": "ACTIVE"}, fields=["name"])
		created_count = 0
		
		for user in active_users:
			exists = frappe.db.exists("rat_user", {"rat_id": self.name, "user_id": user.name})
			if not exists:
				doc = frappe.new_doc("rat_user")
				doc.rat_id = self.name
				doc.user_id = user.name
				doc.insert()
				created_count += 1
		
		frappe.db.commit()
		return created_count

	@frappe.whitelist()
	def get_report_pdf(self):
		from frappe.utils.pdf import get_pdf
		
		# Simple HTML
		hadir = frappe.db.sql("""
			SELECT count(name) FROM `tabrat_user`
			WHERE rat_id = %s AND approved_at IS NOT NULL AND approved_sign IS NOT NULL AND approved_sign != ''
		""", (self.name,))[0][0]

		total_users = frappe.db.count("rat_user", {"rat_id": self.name})
		tidak_hadir = total_users - hadir
		
		# Format Date to Indonesian
		import datetime
		from frappe.utils import getdate, get_datetime
		
		date_obj = getdate(self.date)
		days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
		months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
		
		formatted_date = f"{days[date_obj.weekday()]}, {date_obj.day} {months[date_obj.month - 1]} {date_obj.year}"

		html = """
		<!DOCTYPE html>
		<html>
		<head>
			<title>RAT Report</title>
			<style>
				body {{ font-family: sans-serif; padding: 20px; }}

				h1 {{ 
					color: #333; 
					border-bottom: 2px solid #333; 
					padding-bottom: 10px; 
					text-align: center; 
				}}

				table {{ 
					width: 100%; 
					border-collapse: collapse; 
					margin-top: 20px; 
				}}
				th, td {{ 
					border: 1px solid #ddd; 
					padding: 8px; 
					text-align: left; 
				}}
				th {{ 
					background-color: #f2f2f2; 
				}}
			</style>
		</head>
		<body>

			<h1>RAPAT ANGGOTA TAHUNAN</h1>
			<p style="margin-top: 15px; margin-bottom: 10px; text-align: justify;">
				Berikut adalah ringkasan informasi pelaksanaan Rapat Anggota Tahunan (RAT)
				beserta total Sisa Hasil Usaha (SHU) yang dibagikan.
			</p>
			<table>
				<thead>
					<tr>
						<th>Keterangan</th>
						<th>Detail</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>Periode</td>
						<td>{date}</td>
					</tr>
					<tr>
						<td>Status</td>
						<td>{status}</td>
					</tr>
					<tr>
						<td>Jumlah Anggota</td>
						<td>{jumlah_anggota}</td>
					</tr>
					<tr>
						<td>Jumlah Anggota Hadir</td>
						<td>{jumlah_anggota_hadir}</td>
					</tr>
					<tr>
						<td>Jumlah Anggota Tidak Hadir</td>
						<td>{jumlah_anggota_tidak_hadir}</td>
					</tr>
					<tr>
						<td>Sisa Hasil Usaha Bersih</td>
						<td>{shu_bersih}</td>
					</tr>
					<tr>
						<td>Laba Ditahan</td>
						<td>{laba_ditahan}</td>
					</tr>
					<tr>
						<td>Sisa Hasil Usaha Terbagi</td>
						<td>{shu_terbagi}</td>
					</tr>
					<tr>
						<td>Jasa Modal Terbagi</td>
						<td>{jasa_modal_terbagi}</td>
					</tr>
					<tr>
						<td>Jasa Usaha Terbagi</td>
						<td>{jasa_usaha_terbagi}</td>
					</tr>
					<tr>
						<td>Finalized At</td>
						<td>{finalized_at}</td>
					</tr>
				</tbody>
			</table>

			<p style="margin-top: 20px; text-align: center;">
				<em>This is a generated PDF report.</em>
			</p>

		</body>
		</html>
		""".format(
			name=self.name,
			date=formatted_date,
			status=self.status,
			shu_terbagi=frappe.format_value(self.shu_terbagi, currency=frappe.get_cached_value('Company',  frappe.defaults.get_user_default("Company"),  "default_currency")) if self.shu_terbagi else 0,
			jasa_modal_terbagi=frappe.format_value((self.shu_terbagi*0.4), currency=frappe.get_cached_value('Company',  frappe.defaults.get_user_default("Company"),  "default_currency")) if self.shu_terbagi else 0,
			jasa_usaha_terbagi=frappe.format_value((self.shu_terbagi*0.6), currency=frappe.get_cached_value('Company',  frappe.defaults.get_user_default("Company"),  "default_currency")) if self.shu_terbagi else 0,
			jumlah_anggota=total_users,
			jumlah_anggota_hadir=hadir,
			jumlah_anggota_tidak_hadir=tidak_hadir,
			shu_bersih=frappe.format_value(self.shu_bersih, currency=frappe.get_cached_value('Company',  frappe.defaults.get_user_default("Company"),  "default_currency")) if self.shu_bersih else 0,
			laba_ditahan=frappe.format_value(self.laba_ditahan, currency=frappe.get_cached_value('Company',  frappe.defaults.get_user_default("Company"),  "default_currency")) if self.laba_ditahan else 0,
			sisa_hasil_usaha_terbagi=frappe.format_value(self.shu_terbagi, currency=frappe.get_cached_value('Company',  frappe.defaults.get_user_default("Company"),  "default_currency")) if self.shu_terbagi else 0,
			finalized_at=get_datetime(self.finalize_at).strftime("%d-%m-%Y %H:%M:%S") if self.finalize_at else "",
		)

		pdf = get_pdf(html)
		frappe.local.response.filename = f"{self.name}_report.pdf"
		frappe.local.response.filecontent = pdf
		frappe.local.response.type = "pdf"


	def get_user_financial_data(self, user_id=None, global_data=None):
		"""
		If user_id is None: returns Dict with Global Totals and list of rat_users
		If user_id is set: returns Dict with User Financials. 
		                   If global_data passed, also calculates and returns jasa_modal, jasa_usaha.
		"""
		if user_id is None:
			rat_users = frappe.get_all("rat_user", filters={"rat_id": self.name}, fields=["name", "user_id"])
			user_ids = [d.user_id for d in rat_users]
			
			if not user_ids:
				return {
					'total_saldo_simpanan_wajib': 0,
					'total_saldo_simpanan_pokok': 0,
					'total_nominal_pinjaman': 0,
					'rat_users': [],
					'user_count': 0
				}

			total_saldo_simpanan_wajib = frappe.db.sql("""
				SELECT SUM(saldo) FROM `tabsimpanan_wajib` 
				WHERE profile_id IN %s
			""", (user_ids,))[0][0] or 0
			
			total_saldo_simpanan_pokok = frappe.db.sql("""
				SELECT SUM(saldo) FROM `tabsimpanan_pokok` 
				WHERE profile_id IN %s
			""", (user_ids,))[0][0] or 0
			
			total_nominal_pinjaman = frappe.db.sql("""
				SELECT SUM(t1.nominal) FROM `tabpinjaman` t1
				INNER JOIN `tabpinjaman_pencairan` t2 ON t2.pinjaman_id = t1.name
				WHERE t1.profile_id IN %s AND t2.approved_at IS NOT NULL AND YEAR(t2.approved_at) = %s
			""", (user_ids, self.tahun))[0][0] or 0
			
			return {
				'total_saldo_simpanan_wajib': total_saldo_simpanan_wajib,
				'total_saldo_simpanan_pokok': total_saldo_simpanan_pokok,
				'total_nominal_pinjaman': total_nominal_pinjaman,
				'rat_users': rat_users,
				'user_count': len(rat_users)
			}
		
		# User specific part
		sw = frappe.db.get_value("simpanan_wajib", {"profile_id": user_id}, "saldo") or 0
		sp = frappe.db.get_value("simpanan_pokok", {"profile_id": user_id}, "saldo") or 0
		
		total_pinjaman = frappe.db.sql("""
			SELECT SUM(t1.nominal) FROM `tabpinjaman` t1
			INNER JOIN `tabpinjaman_pencairan` t2 ON t2.pinjaman_id = t1.name
			WHERE t1.profile_id = %s AND t2.approved_at IS NOT NULL AND YEAR(t2.approved_at) = %s
		""", (user_id, self.tahun))[0][0] or 0
		
		result = {
			"simpanan_wajib": sw,
			"simpanan_pokok": sp,
			"pinjaman": total_pinjaman
		}
		
		if global_data:
			total_wajib = global_data.get('total_saldo_simpanan_wajib', 0)
			total_pokok = global_data.get('total_saldo_simpanan_pokok', 0)
			total_global_pinjaman = global_data.get('total_nominal_pinjaman', 0)
			user_count = global_data.get('user_count', 1) # avoid div by zero if empty
			if user_count == 0: user_count = 1

			jasa_modal = ((sw + sp) / (total_wajib + total_pokok)) * (0.4 * self.shu_terbagi) if (total_wajib + total_pokok) != 0 else 0
			
			if total_global_pinjaman != 0:
				jasa_usaha = (total_pinjaman / total_global_pinjaman) * (0.6 * self.shu_terbagi)
			else:
				# If no one has loans, split the 60% portion evenly among all RAT users
				jasa_usaha = (0.6 * self.shu_terbagi) / user_count
			
			result['jasa_modal'] = jasa_modal
			result['jasa_usaha'] = jasa_usaha
			
		return result

	@frappe.whitelist()
	def get_report_excel(self):
		import openpyxl
		from io import BytesIO
		from frappe.utils import flt

		# Create a new workbook and select the active sheet
		wb = openpyxl.Workbook()
		ws = wb.active
		ws.title = "RAT Users"

		# Define headers
		headers = [
			"RAT User ID", "User ID", "Full Name", "SHU Terbagi", 
			"Simpanan Wajib", "Simpanan Pokok","Jasa Modal", "Pinjaman","Jasa Usaha", "Approved At", "Approved Sign"
		]
		ws.append(headers)

		# Get Global Data first required for calculating shares if we wanted to recalculate, 
		# but here we just need user financials. However new method signature supports generic calls.
		# Ideally we iterate over users.
		
		# We can use the global_data fetch primarily to get the list of users if we want, 
		# OR we can just use frappe.get_all as before. 
		# The new method returns 'rat_users' in global data, so let's use that to be efficient?
		# Yes, let's use the new method entirely.
		
		globals_data = self.get_user_financial_data(None)
		rat_users_list = globals_data.get('rat_users', [])

		for row in rat_users_list:
			user_name = frappe.db.get_value("user_profile", row.user_id, "nama") or row.user_id
			
			# We can pass globals_data if we wanted jasa_modal/jasa_usaha separate, for now just financials
			financials = self.get_user_financial_data(row.user_id, globals_data)
			
			# Note: row.shu_terbagi is from the DocType (saved value). 
			# If we wanted the live calculated value we could use financials['jasa_modal'] + financials['jasa_usaha']
			# But report usually shows saved state? Or should it show live?
			# Usually report shows what's in the DB. The previous code showed what's in DB (row.shu_terbagi).
			# I will keep using row.shu_terbagi from the DB but use financials for the other cols.
			# Be careful: 'row' comes from get_all if I use the old way, but here it comes from 'rat_users' list in global_data dict which Was get_all.
			# But get_user_financial_data(None) implementation does:
			# rat_users = frappe.get_all("rat_user", filters={"rat_id": self.name}, fields=["name", "user_id"])
			# It does NOT fetch 'shu_terbagi', 'approved_at', 'approved_sign'.
			# So I need to update get_user_financial_data to fetch those fields if I want to use it here efficienty.
			# OR I just re-fetch here.
			# Let's simple re-fetch here or update the get_all in get_user_financial_data?
			# Using get_all here is safer as get_user_financial_data might be used elsewhere where we don't need all those fields.
			pass

		# Re-fetching to ensure we have all fields for the report
		rat_users = frappe.get_all(
			"rat_user", 
			filters={"rat_id": self.name}, 
			fields=["name", "user_id", "shu_terbagi", "approved_at", "approved_sign"]
		)

		for row in rat_users:
			user_name = frappe.db.get_value("user_profile", row.user_id, "nama") or row.user_id
			
			# Pass globals_data so we COULD calculate things if needed, but primarily to get financials
			financials = self.get_user_financial_data(row.user_id, globals_data)
			
			ws.append([
				row.name,
				row.user_id,
				user_name,
				flt(row.shu_terbagi),
				financials['simpanan_wajib'],
				financials['simpanan_pokok'],
				financials['jasa_modal'],
				financials['pinjaman'],
				financials['jasa_usaha'],
				row.approved_at,
				row.approved_sign
			])

		# Save to buffer
		output = BytesIO()
		wb.save(output)
		output.seek(0)

		# Set response
		frappe.local.response.filename = f"Report RAT_{self.date.strftime('%d-%m-%Y')}.xlsx"
		frappe.local.response.filecontent = output.read()
		frappe.local.response.type = "binary"
		
		
