import frappe

# Function that creates Predictive Maintenance on Submit of Maintenance Schedule
def create_docs_on_submit(self, method=None):
    schedules_list = self.schedules
    if len(schedules_list) > 0:
        for schedule in schedules_list:
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
            current_allowed_occurance = frappe.db.get_value("Item", schedule.item_code, 'custom_allowed_simultaneous_occurance')
            if current_allowed_occurance != 0:
                pairs = frappe.db.sql(
                    '''
                        SELECT 
                            tmsd.parent, tmsd.item_code, tmsd.scheduled_date, tmsd.custom_scheduled_end_date 
                        FROM 
                            `tabMaintenance Schedule Detail` tmsd 
                        WHERE 
                            tmsd.item_code  = '{0}' 
                        AND 
                            tmsd.scheduled_date = '{1}' 
                        AND 
                            tmsd.custom_scheduled_end_date = '{2}';
                    '''.format(schedule.item_code, schedule.scheduled_date, schedule.custom_scheduled_end_date)
                , as_dict = 1)
                current_total_pairs = len(pairs)

                if current_total_pairs >= current_allowed_occurance:
                    frappe.throw("Only {0} Simultaneous Occurance are allowed for Item {1}".format(current_allowed_occurance, frappe.bold(schedule.item_code)))

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