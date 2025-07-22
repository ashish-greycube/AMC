frappe.ui.form.on("Maintenance Schedule", {
    refresh(frm) {
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button('Update Customer Contact', function () {
                let d = new frappe.ui.Dialog({
                    title: "Enter New Contact Details",
                    fields: [
                        {
                            label: 'Current Details',
                            fieldname: 'custom_start_section_break',
                            fieldtype: 'Section Break',
                        },
                        {
                            label: 'Contact Person',
                            fieldname: 'contact_person',
                            fieldtype: 'Link',
                            options: 'Contact',
                            default: frm.doc.contact_person,
                            read_only: 1
                        },
                        {
                            label: 'Contact Mobile',
                            fieldname: 'contact_phone',
                            fieldtype: 'Data',
                            options: 'Phone',
                            default: frm.doc.contact_mobile,
                            read_only: 1
                        },
                        {
                            label: 'Contact Email',
                            fieldname: 'contact_email',
                            fieldtype: 'Data',
                            options: 'Email',
                            default: frm.doc.contact_email,
                            read_only: 1
                        },
                        {
                            label: 'Enter Updated Details',
                            fieldname: 'custom_section_break',
                            fieldtype: 'Section Break',
                        },
                        {
                            label: 'Contact Person',
                            fieldname: 'updated_contact_person',
                            fieldtype: 'Link',
                            options: 'Contact',
                            get_query: function () {
                                return {
                                    query: 'amc.api.get_contact_person_query',
                                    filters: {
                                        'customer': frm.doc.customer
                                    }
                                }
                            },
                            onchange: function () {
                                let contact_person = d.get_field("updated_contact_person").value

                                frappe.db.get_doc('Contact', contact_person)
                                    .then(doc => {
                                        let phone_no = doc.phone_nos[0].phone
                                        d.set_value('updated_contact_mobile', phone_no)
                                    })

                                frappe.db.get_doc('Contact', contact_person)
                                    .then(doc => {
                                        let email = doc.email_ids[0].email_id
                                        d.set_value('updated_contact_email', email)
                                    })
                            }
                        },
                        {
                            label: 'Contact Mobile',
                            fieldname: 'updated_contact_mobile',
                            fieldtype: 'Data',
                            options: 'Phone'
                        },
                        {
                            label: 'Contact Email',
                            fieldname: 'updated_contact_email',
                            fieldtype: 'Data',
                            options: 'Email'
                        },
                    ],
                    primary_action_label: 'Update',
                    primary_action(values) {
                        frappe.call({
                            method: 'amc.api.update_contact_in_pm',
                            args: {
                                'parent' : cur_frm.doc.name,
                                'new_contact_person' : values.updated_contact_person,
                                'new_contact_phone' : values.updated_contact_mobile,
                                'new_contact_email' : values.updated_contact_email,
                            },
                            callback:function(r){
                                frm.reload_doc()
                            }
                        })
                        d.hide();
                    }
                })
                d.show()
            })
        }
    },
});

frappe.ui.form.on("Maintenance Schedule Detail", {
    update_btn(frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        console.log(row)
        let d = new frappe.ui.Dialog({
            title: 'Enter New Details',
            fields: [
                {
                    label: 'Current Details',
                    fieldname: 'custom_start_section_break',
                    fieldtype: 'Section Break',
                },
                {
                    label: 'Schedule Start Date',
                    fieldname: 'scheduled_date',
                    fieldtype: 'Date',
                    default: row['scheduled_date'],
                    read_only: 1
                },
                {
                    label: 'Item Code',
                    fieldname: 'item_code',
                    fieldtype: 'Data',
                    default: row['item_code'],
                    read_only: 1
                },
                {
                    label: '',
                    fieldname: 'date_col_break',
                    fieldtype: 'Column Break',
                },
                {
                    label: 'Schedule End Date',
                    fieldname: 'scheduled_end_date',
                    fieldtype: 'Date',
                    default: row['custom_scheduled_end_date'],
                    read_only: 1
                },
                {
                    label: 'Item Qty',
                    fieldname: 'item_qty',
                    fieldtype: 'Data',
                    default: row['qty'],
                    read_only: 1
                },
                {
                    label: 'Enter Updated Details',
                    fieldname: 'custom_section_break',
                    fieldtype: 'Section Break',
                },
                {
                    label: 'Schedule Start Date',
                    fieldname: 'updated_scheduled_date',
                    fieldtype: 'Date',
                },
                {
                    label: 'Schedule End Date',
                    fieldname: 'updated_scheduled_end_date',
                    fieldtype: 'Date',
                },
                {
                    label: 'Reschedule Reason',
                    fieldname: 'reschedule_reason',
                    fieldtype: 'Link',
                    reqd: 1,
                    default: row['custom_reschedule_reason'],
                    options: 'TIEPL Reschedule Reason'
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {

                if (cur_frm.doc.custom_branch == null) {
                    d.hide();
                    frappe.throw('Branch is Not Selected!');
                }
                else {
                    frappe.call({
                        method: 'amc.api.update_predictive_data_after_submit',
                        args: {
                            'doctype': row['doctype'],
                            'docname': row['name'],
                            'predictive_doc': row['custom_amc_schedule_reference'],
                            'reschedule_reason': values.reschedule_reason,
                            'updated_schedule_date': values.updated_scheduled_date,
                            'updated_scheduled_end_date': values.updated_scheduled_end_date,
                            'item_code': values.item_code,
                            'branch': cur_frm.doc.custom_branch,
                            'parent': row['parent'],
                            'idx' : row['idx']
                        },
                        callback: function (r) {
                            frm.reload_doc()
                        }
                    })
                }

                d.hide();
            }
        });
        d.show();
    },
});