import frappe

# Function that creates Predictive Maintenance on Submit of Maintenance Schedule
def create_docs_on_submit(self, method=None):
    schedules_list = self.schedules
    if len(schedules_list) > 0:
        for schedule in schedules_list:
            sp_email = ""
            employee_id = frappe.db.get_value('Sales Person', schedule.sales_person, 'employee')
            if employee_id != None:
                sp_email = frappe.db.get_value('Employee', employee_id, 'prefered_email')

            sd_doc = frappe.new_doc('Predictive Maintenance')
            sd_doc.item_code = schedule.item_code
            sd_doc.item_name = schedule.item_name
            sd_doc.scheduled_date = schedule.scheduled_date
            sd_doc.scheduled_end_date = schedule.custom_scheduled_end_date
            sd_doc.sales_person = schedule.sales_person
            sd_doc.customer = self.customer_name
            sd_doc.completion_status = schedule.completion_status
            sd_doc.subject = "{0} - {1}".format(self.customer_name, schedule.item_name,)
            sd_doc.customer_email = self.custom_customer_email
            sd_doc.description = schedule.custom_remark
            sd_doc.contact_person = self.contact_person
            sd_doc.mobile_no = self.contact_mobile
            sd_doc.contact_email = self.contact_email
            sd_doc.sales_order_reference = self.sales_order_cf
            sd_doc.maintenance_schedule_reference = self.name
            sd_doc.sales_person_email = sp_email
            sd_doc.insert(ignore_permissions=True)
        
            frappe.db.set_value('Maintenance Schedule Detail', schedule.name, 'custom_amc_schedule_reference', sd_doc.name)

# Function that deletes Predictive Maintenance on cancel of Maintenance Schedule
def delete_docs_on_cancel(self, method=None):
    schedules_list = self.schedules
    if len(schedules_list) > 0:
        for schedule in schedules_list:
            if schedule.custom_amc_schedule_reference != None:
                frappe.delete_doc('Predictive Maintenance', schedule.custom_amc_schedule_reference)
           
# Function for equipement validation (Item-Date Pair)
def validate_occurance(self, method=None):
    schedules_list = self.schedules
    if len(schedules_list) > 0:
        for schedule in schedules_list:
            current_allowed_occurance = frappe.db.get_value(
                                            doctype = "Branch Wise Equipment Occurrence", 
                                            filters = {
                                                'parent': schedule.item_code,
                                                'branch': self.custom_branch, 
                                                'parenttype':'Item'
                                            }, 
                                            fieldname = 'no_of_simultaneous_occurrence'
                                        )
            if current_allowed_occurance != 0 and current_allowed_occurance != None:
                pairs = frappe.db.sql(
                    '''
                        SELECT 
                            tmsd.parent, tmsd.item_code, tmsd.scheduled_date, tmsd.custom_scheduled_end_date 
                        FROM 
                            `tabMaintenance Schedule Detail` tmsd 
                        INNER JOIN
                            `tabMaintenance Schedule` tms
                        ON 
                            tms.name = tmsd.parent
                        WHERE 
                            tmsd.item_code  = '{0}' 
                        AND
                            tms.custom_branch = '{3}'
                        AND 
                            tmsd.scheduled_date = '{1}' 
                        AND 
                            tmsd.custom_scheduled_end_date = '{2}'
                        AND 
                            tms.name != '{4}';
                    '''.format(schedule.item_code, schedule.scheduled_date, schedule.custom_scheduled_end_date, self.custom_branch, self.name)
                , as_dict = 1)
                current_total_pairs = len(pairs)

                if current_total_pairs >= current_allowed_occurance:
                    frappe.throw("In Row {0}: Simultaneous Occurrence for Item {1} Exceeds Permitted Occurence {2}".format(schedule.idx, frappe.bold(schedule.item_code), current_allowed_occurance))

# Function for set SO in Maintenance Schedule at Parent Level 
def set_sales_order(self, method=None):
    if len(self.items) > 0:
        sales_order = self.items[0].sales_order
    self.sales_order_cf = sales_order

# Function for set SO in Maintenance Visit
def set_sales_order_in_ms_visit(self, method=None):
    if self.sales_order_cf:
        so = self.sales_order_cf
        if len(self.purposes) > 0:
            for purpose in self.purposes:
                purpose.prevdoc_doctype = 'Sales Order'
                purpose.prevdoc_docname = so
    
# Function for set qty in MS Schedule Table
def set_qty_in_ms_schedule(self, method=None):
    if len(self.items) > 0:
        for item in self.items:
            for schedule in self.schedules:
                if schedule.item_code == item.item_code:
                    if schedule.qty == 0:
                        schedule.qty = item.qty

@frappe.whitelist()
def update_predictive_data_after_submit(doctype, docname, predictive_doc, reschedule_reason, updated_schedule_date, updated_scheduled_end_date,  item_code, branch, parent):
    # Check For Equipement Validation
    current_allowed_occurance = frappe.db.get_value(
                                            doctype = "Branch Wise Equipment Occurrence", 
                                            filters = {
                                                'parent': item_code,
                                                'branch': branch, 
                                                'parenttype':'Item'
                                            }, 
                                            fieldname = 'no_of_simultaneous_occurrence'
                                        )
    pairs = frappe.db.sql(
        '''
            SELECT 
                tmsd.parent, tmsd.item_code, tmsd.scheduled_date, tmsd.custom_scheduled_end_date 
            FROM 
                `tabMaintenance Schedule Detail` tmsd 
            INNER JOIN
                `tabMaintenance Schedule` tms
            ON 
                tms.name = tmsd.parent
            WHERE 
                tmsd.item_code  = '{0}' 
            AND
                tms.custom_branch = '{3}'
            AND 
                tmsd.scheduled_date = '{1}' 
            AND 
                tmsd.custom_scheduled_end_date = '{2}'
            AND 
                tms.name != '{4}';
        '''.format(item_code, updated_schedule_date, updated_scheduled_end_date, branch, parent)
    , as_dict = 1)
    current_total_pairs = len(pairs)

    if current_total_pairs >= current_allowed_occurance:
        frappe.throw("Simultaneous Occurrence for Item {0} Exceeds Permitted Occurence {1}".format(frappe.bold(item_code), current_allowed_occurance))
    else:
        # Updating Child Table Data
        frappe.db.set_value(doctype, docname, 'scheduled_date', updated_schedule_date)
        frappe.db.set_value(doctype, docname, 'custom_scheduled_end_date', updated_scheduled_end_date)
        frappe.db.set_value(doctype, docname, 'custom_reschedule_reason', reschedule_reason)

        # Updating Predictive Maintenance Data
        frappe.db.set_value('Predictive Maintenance', predictive_doc, 'scheduled_date', updated_schedule_date)
        frappe.db.set_value('Predictive Maintenance', predictive_doc, 'scheduled_end_date', updated_scheduled_end_date)