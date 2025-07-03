frappe.ui.form.on("Maintenance Schedule", {
    refresh(frm) {
    
    },
});

frappe.ui.form.on("Maintenance Schedule Detail", {
    update_btn(frm,cdt,cdn) {
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
                    fieldtype: 'Small Text',
                    reqd: 1,
                    default: row['custom_reschedule_reason']
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                console.log(values);
                frappe.call({
                    method: 'amc.api.update_predictive_data_after_submit',
                    args: {
                        'doctype' : row['doctype'],
                        'docname' : row['name'],
                        'predictive_doc' : row['custom_amc_schedule_reference'],
                        'reschedule_reason' : values.reschedule_reason,
                        'updated_schedule_date' : values.updated_scheduled_date,
                        'updated_scheduled_end_date' : values.updated_scheduled_end_date,
                        'item_code' : values.item_code,
                        'branch' : cur_frm.doc.custom_branch,
                        'parent' : row['parent']
                    },
                    callback: function(r) {
                        frm.reload_doc()
                    }
                })
                d.hide();
            }
        });
        d.show();
    },
});