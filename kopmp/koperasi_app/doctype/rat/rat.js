// Copyright (c) 2026, . and contributors
// For license information, please see license.txt
frappe.ui.form.on("rat", {
    refresh(frm) {
        frm.add_custom_button(__("Hitung SHU"), function () {
            frm.call({
                doc: frm.doc,
                method: "hitung_shu_anggota",
                callback: function (r) {
                    if (r.message) {
                        console.log("SHU Calculation Results:", r.message);
                        r.message.forEach(member => {
                            console.log(`User: ${member.user_id}`);
                            console.log(`- RAT User ID: ${member.rat_user}`);
                            console.log(`- Simpanan Wajib: ${member.simpanan_wajib}`);
                            console.log(`- Simpanan Pokok: ${member.simpanan_pokok}`);
                            console.log(`- Pinjaman: ${member.pinjaman}`);
                            console.log(`- Jasa Modal: ${member.jasa_modal}`);
                            console.log(`- Jasa Usaha: ${member.jasa_usaha}`);
                            console.log(`- Total Simpanan Wajib: ${member.total_saldo_simpanan_wajib_All}`);
                            console.log(`- Total Simpanan Pokok: ${member.total_saldo_simpanan_pokok_All}`);
                            console.log(`- Total Pinjaman: ${member.total_nominal_pinjaman_All}`);
                            console.log('-------------------');
                        });
                        frappe.msgprint("Calculation results logged to console.");
                    }
                }
            });
        });

        frm.add_custom_button(__("Generate RAT Users"), function () {
            frm.call({
                doc: frm.doc,
                method: "create_rat_users",
                freeze: true,
                freeze_message: __("Creating RAT Users..."),
                callback: function (r) {
                    if (r.message) {
                        frappe.msgprint(__("Created {0} RAT Users", [r.message]));
                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__("No new RAT Users created."));
                    }
                }
            });
        });
        // frm.add_custom_button(__("Report"), function () {
        //     let url = frappe.urllib.get_full_url(
        //         "/api/method/run_doc_method?" +
        //         frappe.utils.get_query_string({
        //             dt: frm.doc.doctype,
        //             dn: frm.doc.name,
        //             method: "get_report_pdf"
        //         })
        //     );
        //     window.open(url);
        // });
        // Optional: only after submit if needed
        // if (frm.doc.docstatus !== 1) return;

        frm.add_custom_button(__("Report RAT"), () => {
            const url = frappe.urllib.get_full_url(
                "/api/method/run_doc_method?" +
                $.param({
                    dt: frm.doc.doctype,
                    dn: frm.doc.name,
                    method: "get_report_pdf"
                })
            );

            window.open(url);
        });

        frm.add_custom_button(__("Report Anggota"), () => {
            const url = frappe.urllib.get_full_url(
                "/api/method/run_doc_method?" +
                $.param({
                    dt: frm.doc.doctype,
                    dn: frm.doc.name,
                    method: "get_report_excel"
                })
            );

            window.open(url);
        });
    },
});
