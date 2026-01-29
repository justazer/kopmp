frappe.ui.form.on("Pinjaman Pencairan", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.page.btn_secondary.hide();
        }
        if (frm.doc.docstatus === 0 && !frm.doc.__islocal) {
            // Check if parent Pinjaman is approved
            frappe.db.get_value('Pinjaman', frm.doc.pinjaman_id, 'status')
                .then(r => {
                    if (r && r.message.status === 'Approved') {
                        frm.add_custom_button(__('Approve'), function () {
                            frm.set_value('status', 'Disbursed'); // Assuming Disbursed is the approved state for Pencairan
                            frm.set_value('approved_at', frappe.datetime.now_datetime());
                            frm.save('Submit');
                        }).addClass('btn-primary');

                        frm.add_custom_button(__('Reject'), function () {
                            frm.set_value('status', 'Rejected');
                            frm.save('Submit');
                        }).addClass('btn-danger');
                    }
                });
        }
    }
});
