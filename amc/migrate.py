import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.page.setup_wizard.setup_wizard import make_records

def after_migrate():
    custom_fields = {
        "Maintenance Schedule Detail" : [
            {
                'fieldname': 'custom_scheduled_end_date',
                'fieldtype': 'Date',
                'label': _('Scheduled End Date'),
                'insert_after' : 'scheduled_date',
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'in_list_view': 1,
            },
            {
                'fieldname': 'custom_amc_schedule_reference',
                'fieldtype': 'Data',
                'label': _('Predictive Maintenance Reference'),
                'insert_after' : 'item_reference',
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'allow_on_submit': 1,
                'read_only': 1,
            },
            {
                'fieldname' : 'qty',
                'fieldtype' : 'Float',
                'label' : _('Schedule Qty'),
                'insert_after' : 'item_name',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
            {
                'fieldname' : 'update_btn',
                'fieldtype' : 'Button',
                'label' : _('Update'),
                'insert_after' : 'custom_amc_schedule_reference',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'depends_on': 'eval:doc.actual_date==null && doc.docstatus==1;'
            },
            {
                'fieldname' : 'custom_reschedule_reason',
                'fieldtype' : 'Link',
                'label' : _('Reschedule Reason'),
                'insert_after' : 'actual_date',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'allow_on_submit' : 1,
                'options': 'TIEPL Reschedule Reason'
            },
            {
                'fieldname' : 'custom_sales_person_email',
                'fieldtype' : 'Data',
                'label' : _('Sales Person Email'),
                'insert_after' : 'sales_person',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
            },
        ],

        "Maintenance Schedule Item" : [
            {
                'fieldname': 'qty',
                'fieldtype': 'Float',
                'label': _('Quantity'),
                'insert_after' : 'end_date',
                'is_system_generated' : 0,
                'is_custom_field': 1,
            }
        ],

        "Maintenance Schedule": [
            {
                'fieldname': 'sales_order_cf',
                'fieldtype': 'Link',
                'label' : _('Sales Order'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'read_only': 1,
                'options' : 'Sales Order',
                'insert_after' : 'company'
            },
            {
                'fieldname': 'custom_customer_email',
                'fieldtype': 'Data',
                'label' : _('Customer Email'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'options' : 'Email',
                'insert_after' : 'customer'
            },
            {
                'fieldname': 'custom_branch',
                'fieldtype': 'Link',
                'label' : _('Branch'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'options' : 'Branch',
                'insert_after' : 'transaction_date'
            },
             {
                'fieldname' : 'custom_sp_email',
                'fieldtype' : 'Data',
                'label' : _('Sales Person Email'),
                'insert_after' : 'sales_order_cf',
                'is_custom_field' : 1,
                'is_system_generated' : 0,
                'read_only' : 1,
                'hidden' : 1,
                'options' : 'Email'
            },
        ],

        "Maintenance Visit" : [
            {
                'fieldname': 'custom_period_of_service',
                'fieldtype': 'Data',
                'label': _('Period Of Service'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'completion_status',
                'reqd' : 1
            }, 
            {
                'fieldname': 'custom_system_voltage',
                'fieldtype': 'Link',
                'label': _('System Voltage'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'maintenance_type',
                'options' : 'TIEPL System Voltage',
                'reqd' : 1
            },
            {
                'fieldname': 'custom_control_voltage',
                'fieldtype': 'Link',
                'label': _('Control Voltage'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_period_of_service',
                'options' : 'TIEPL Control Voltage',
                'reqd' : 1
            }, 
            {
                'fieldname': 'custom_recommendation',
                'fieldtype': 'Small Text',
                'label': _('Recommendation'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'customer_feedback',
                'reqd' : 1
            }, 
            {
                'fieldname': 'custom_remarks',
                'fieldtype': 'Small Text',
                'label': _('Remarks'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_recommendation',
                'reqd' : 1
            }, 
            {
                'fieldname': 'custom_abnormality',
                'fieldtype': 'Select',
                'label': _('Abnormality'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'company',
                'options' : '\nYes\nNo',
                'reqd' : 1
            }, 
            {
                'fieldname': 'custom_rating_by_customer',
                'fieldtype': 'Select',
                'label': _('Rating By Customer'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_abnormality',
                'options' : '\nVery Poor\nPoor\nAverage\nGood\nExcellent',
                'reqd' : 1
            },  
            {
                'fieldname': 'custom_signature_block',
                'fieldtype': 'Section Break',
                'label': _('Signature Info'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'amended_from',
            }, 
            {
                'fieldname': 'custom_service_person',
                'fieldtype': 'Link',
                'label': _('Service Person'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_signature_block',
                'options' : 'User',
                'reqd' : 1
            },
            {
                'fieldname': 'custom_service_person_signature',
                'fieldtype': 'Signature',
                'label': _('Service Person Signature'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_service_person',
                'reqd' : 1
            },
            {
                'fieldname': 'custom_signature_column_break',
                'fieldtype': 'Column Break',
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_service_person_signature',
            }, 
            {
                'fieldname': 'custom_customer_representative',
                'fieldtype': 'Data',
                'label': _('Customer Representative'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_signature_column_break',
                'reqd' : 1
            },
            {
                'fieldname': 'custom_customer_representative_signature',
                'fieldtype': 'Signature',
                'label': _('Customer Representative Signature'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_customer_representative',
                'reqd' : 1
            },
        ],
        
        "Item" : [
            {
                'fieldname' : 'custom_allowed_simultaneous_occurance',
                'fieldtype' : 'Int',
                'label' : _('Allowed Simultaneous Occurance'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'stock_uom',
                'default' : 0
            },
            {
                'fieldname' : 'custom_sb_branchs',
                'fieldtype' : 'Section Break',
                'label' : _('Equipement Occurance'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'brand',
                'collapsible' : 1
            },
            {
                'fieldname' : 'custom_equipement_occurence',
                'fieldtype' : 'Table',
                'label' : _('Branch and Equipement Occurence'),
                'is_system_generated' : 0,
                'is_custom_field': 1,
                'insert_after' : 'custom_sb_branchs',
                'options' : 'Branch Wise Equipment Occurrence',
            }
        ],

        "Issue": [
            {
                'fieldname': 'custom_customer_representative',
                'fieldtype': 'Data',
                'label' : _('Customer Representative'),
                'is_custom_field': 1,
                'is_system_generated' : 0,
                'insert_after' : 'customer_feedback_cf',
            }
        ]
    }

    print("Adding Custom Fields In MS.....")
    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)