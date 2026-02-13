// Copyright (c) 2026, . and contributors
// For license information, please see license.txt

frappe.ui.form.on("rat_user", {
    refresh: function (frm) {
        if (frm.doc.user_id) {
            frm.fields_dict['pencairan'].grid.update_docfield_property('rat_user_id', 'read_only', 1);
        }

        // if (!frm.doc.approved_at) {
        frm.add_custom_button(__("Make Token"), function () {
            frm.call({
                method: 'generate_token_rat',
                doc: frm.doc,
                callback: function (r) {
                    if (r.message) {
                        frappe.msgprint(__("Your Token: {0}", [r.message]));
                    }
                }
            });
        }).addClass("btn-primary");
        // }
    },
    user_id: function (frm) {
        if (frm.doc.user_id) {
            frm.fields_dict['pencairan'].grid.update_docfield_property('rat_user_id', 'read_only', 1);
            let saldo_wajib = 0;
            let saldo_pokok = 0;
            let saldo_pinjaman = 0;
            let jumlah_rat_user = 0;
            let shu_rat_terbagi = 0;

            // Fetch Jumlah RAT User
            frappe.db.count("rat_user")
                .then(count => {
                    jumlah_rat_user = count;
                    console.log("Jumlah RAT User Variable:", jumlah_rat_user);
                });

            // Fetch shu terbagi
            //if (frm.doc.rat_id) {
            frappe.db.get_value("rat", frm.doc.rat_id, "shu_terbagi")
                .then(r => {
                    if (r && r.message && r.message.shu_terbagi) {
                        shu_rat_terbagi = r.message.shu_terbagi;
                    } else {
                        shu_rat_terbagi = 0;
                    }
                    console.log("SHU RAT Terbagi Variable:", shu_rat_terbagi);
                });
            //}

            // Fetch Saldo Simpanan Wajib
            frappe.db.get_value("simpanan_wajib", { profile_id: frm.doc.user_id }, "saldo")
                .then(r => {
                    if (r && r.message && r.message.saldo) {
                        saldo_wajib = r.message.saldo;
                    } else {
                        saldo_wajib = 0;
                    }
                    console.log("Saldo Wajib Variable:", saldo_wajib);
                });

            // Fetch Saldo Simpanan Pokok
            frappe.db.get_value("simpanan_pokok", { profile_id: frm.doc.user_id }, "saldo")
                .then(r => {
                    if (r && r.message && r.message.saldo) {
                        saldo_pokok = r.message.saldo;
                    } else {
                        saldo_pokok = 0;
                    }
                    console.log("Saldo Pokok Variable:", saldo_pokok);
                });

            frappe.db.get_value("pinjaman", { profile_id: frm.doc.user_id }, "nominal")
                .then(r => {
                    if (r && r.message && r.message.nominal) {
                        saldo_pinjaman = r.message.nominal;
                    } else {
                        saldo_pinjaman = 0;
                    }
                    console.log("Saldo Pinjaman Variable:", saldo_pinjaman);
                });
        }
    }
});

frappe.ui.form.on("rat_user_pencairan", {
    pencairan_add: function (frm, cdt, cdn) {
        if (frm.doc.name) {
            frappe.model.set_value(cdt, cdn, "rat_user_id", frm.doc.name);
        }
    }
});
