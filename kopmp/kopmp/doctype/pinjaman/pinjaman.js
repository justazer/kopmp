// Copyright (c) 2026, Administrator and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pinjaman", {
    refresh(frm) {
        if (frm.doc.pinjaman_produk_id) {
            frm.trigger('set_top_options');
        }
    },
    pinjaman_produk_id(frm) {
        frm.set_value('top', ''); // Clear existing value
        frm.set_value('rate', ''); // Clear rate as well
        if (frm.doc.pinjaman_produk_id) {
            frm.trigger('set_top_options');
        } else {
            frm.set_df_property('top', 'options', []);
        }
    },
    top(frm) {
        if (frm.doc.top && frm.top_rates) {
            let rate = frm.top_rates[frm.doc.top.toString()];
            if (rate !== undefined) {
                frm.set_value('rate', rate);
            }
        }
    },
    set_top_options(frm) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Pinjaman Produk Top",
                filters: {
                    pinjaman_produk_id: frm.doc.pinjaman_produk_id
                },
                fields: ["top", "rate"],
                order_by: "top asc"
            },
            callback: function (r) {
                if (r.message) {
                    frm.top_rates = {};
                    r.message.forEach(d => {
                        frm.top_rates[d.top.toString()] = d.rate;
                    });

                    let options = r.message.map(d => d.top.toString());
                    // Add existing value if not in options (to avoid data loss on view)
                    if (frm.doc.top && !options.includes(frm.doc.top.toString())) {
                        options.push(frm.doc.top.toString());
                    }
                    frm.set_df_property('top', 'options', options.join('\n'));
                } else {
                    frm.set_df_property('top', 'options', []);
                    frm.top_rates = {};
                }
            }
        });
    }
});
