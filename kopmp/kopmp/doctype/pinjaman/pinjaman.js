// Copyright (c) 2026, Administrator and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pinjaman", {
    onload(frm) {
        frm.set_value('request_at', frappe.datetime.now_datetime());
    },
    refresh(frm) {
        if (frm.doc.pinjaman_produk_id) {
            frm.trigger('set_top_options');
        }

        // Aggressively hide Submit button
        setTimeout(() => {
            // frm.page.remove_inner_button('Submit');
            // frm.page.remove_inner_button(__("Submit"));

            // CSS/jQuery fallback
            frm.page.wrapper.find('button[data-label="Submit"]').hide();
            frm.page.wrapper.find('button:contains("Submit")').hide();

            if (frm.page.btn_secondary) {
                frm.page.btn_secondary.hide();
            }
        }, 100);

        // Polling to ensure it stays hidden if re-rendered
        let hideSubmitInterval = setInterval(() => {
            if (frm.page.wrapper.find('button[data-label="Submit"]').is(":visible")) {
                frm.page.remove_inner_button('Submit');
                frm.page.wrapper.find('button[data-label="Submit"]').hide();
            }
        }, 1000);

        // Clear interval after some time to avoid performance hit
        setTimeout(() => clearInterval(hideSubmitInterval), 10000);

        if (frm.doc.status === 'Requested' && !frm.doc.__islocal) {
            frm.add_custom_button(__('Approve'), function () {
                frm.set_value('status', 'Approved');
                frm.set_value('approved_at', frappe.datetime.now_datetime());
                frm.enable_save();
                frm.save('Submit');
            }).addClass('btn-primary');

            frm.add_custom_button(__('Reject'), function () {
                frm.set_value('status', 'Rejected');
                frm.enable_save();
                frm.save('Submit'); // or just save if you don't want to lock it
            }).addClass('btn-danger');
        }
    },
    pinjaman_produk_id(frm) {
        frm.set_value('top', ''); // Clear existing value
        frm.set_value('rate', ''); // Clear rate as well
        frm.set_value('start_date', '');
        frm.set_value('end_date', '');
        if (frm.doc.pinjaman_produk_id) {
            frm.trigger('set_top_options');
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Pinjaman Produk",
                    name: frm.doc.pinjaman_produk_id
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('start_date', r.message.start_date);
                        frm.set_value('end_date', r.message.end_date);
                    }
                }
            });
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
    // set_start_end(frm) {
    //     frappe.call({
    //         method: "frappe.client.get_list",
    //         args: {
    //             doctype: "Pinjaman Produk",
    //             filters: {
    //                 name: frm.doc.pinjaman_produk_id
    //             },
    //             fields: ["start_date", "end_date"],
    //             order_by: "start_date asc"
    //         },
    //         callback: function (r) {
    //             if (r.message) {
    //                 frm.top_rates = {};
    //                 r.message.forEach(d => {
    //                     frm.top_rates[d.top.toString()] = d.rate;
    //                 });

    //                 let options = r.message.map(d => d.top.toString());
    //                 // Add existing value if not in options (to avoid data loss on view)
    //                 if (frm.doc.top && !options.includes(frm.doc.top.toString())) {
    //                     options.push(frm.doc.top.toString());
    //                 }
    //                 frm.set_df_property('top', 'options', options.join('\n'));
    //             } else {
    //                 frm.set_df_property('top', 'options', []);
    //                 frm.top_rates = {};
    //             }
    //         }
    //     });
    // }
});
