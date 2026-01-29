frappe.ui.form.on("Pinjaman Installment", {
    refresh(frm) {
        frm.disable_save();
        if (!frm.doc.paid_date && !frm.doc.__islocal) {
            frm.add_custom_button(__('Paid'), function () {
                frappe.confirm('Are you sure you want to mark this installment as Paid?', () => {
                    frm.set_value('paid_date', frappe.datetime.now_date());
                    frm.set_value('paid_pokok', frm.doc.nominal_pokok);
                    frm.set_value('paid_bunga', frm.doc.nominal_bunga);
                    frm.set_value('paid_denda', frm.doc.nominal_denda);
                    frm.enable_save();
                    frm.save();
                });
            }).addClass('btn-primary');
        }
    }
});
