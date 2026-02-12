frappe.ui.form.on("Pinjaman Installment", {
    refresh(frm) {
        if (!frm.doc.__islocal && frm.doc.payment_status !== 'Paid') {
            frm.add_custom_button(__('Paid'), function () {
                frappe.confirm('Are you sure you want to mark this installment as Paid?', () => {
                    frappe.call({
                        doc: frm.doc,
                        method: 'set_paid',
                        callback: function (r) {
                            frm.reload_doc();
                        }
                    });
                });
            }).addClass('btn-primary');
        }
    }
});
