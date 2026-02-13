// Copyright (c) 2026, . and contributors
// For license information, please see license.txt

frappe.ui.form.on("simpanan_wajib_log", {
    simpanan_wajib_id: function (frm) {
        if (frm.doc.simpanan_wajib_id) {
            frappe.db.get_value("simpanan_wajib", frm.doc.simpanan_wajib_id, "saldo")
                .then(r => {
                    if (r && r.message) {
                        frm.set_value("saldo_awal", r.message.saldo);
                        if (frm.doc.nominal) {
                            frm.trigger("nominal");
                        }
                    }
                });
        }
    },
    nominal: function (frm) {
        let saldo_awal = frm.doc.saldo_awal || 0;
        let nominal = frm.doc.nominal || 0;
        frm.set_value("saldo_akhir", saldo_awal + nominal);
    }
});
