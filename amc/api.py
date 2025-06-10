import frappe

# Function that creates AMC Schedule on Submit of Maintenance Schedule
def create_docs_on_submit(self, method=None):
    schedules_list = self.schedules
    if len(schedules_list) > 0:
        for schedule in schedules_list:
            sd_doc = frappe.new_doc('AMC Schedule')
            sd_doc.item_code = schedule.item_code
            sd_doc.item_name = schedule.item_name
            sd_doc.scheduled_date = schedule.scheduled_date
            sd_doc.scheduled_end_date = schedule.custom_scheduled_end_date
            sd_doc.sales_person = schedule.sales_person
            sd_doc.customer = self.customer_name
            sd_doc.completion_status = schedule.completion_status
            sd_doc.subject = "{0}-{1} ({2})".format(schedule.item_name, schedule.sales_person, self.customer_name)
            sd_doc.insert()

            frappe.db.set_value('Maintenance Schedule Detail', schedule.name, 'custom_amc_schedule_reference', sd_doc.name)

# Function that deletes AMC Schedule on cancel of Maintenance Schedule
def delete_docs_on_cancel(self, method=None):
    schedules_list = self.schedules
    if len(schedules_list) > 0:
        for schedule in schedules_list:
            if schedule.custom_amc_schedule_reference != None:
                frappe.delete_doc('AMC Schedule', schedule.custom_amc_schedule_reference)
           

# Function for Validating Sales Person
def validate_sales_person(self, method=None):
    schedules_list = self.schedules
    if len(schedules_list) > 0:
        for schedule in schedules_list:
            start_date = schedule.scheduled_date
            end_date = schedule.custom_scheduled_end_date

            sales_persons = frappe.db.sql(f'''
                SELECT 
                    DISTINCT(tmsd.sales_person)
                FROM 
                    `tabMaintenance Schedule Detail` tmsd
                WHERE 
                    (((tmsd.scheduled_date  BETWEEN "{start_date}" AND "{end_date}") OR (tmsd.custom_scheduled_end_date BETWEEN "{start_date}" AND "{end_date}"))AND tmsd.docstatus = 1)
                OR 
                    ((tmsd.custom_scheduled_end_date >= "{start_date}") AND (tmsd.custom_scheduled_end_date <= "{end_date}") AND tmsd.docstatus = 1)
                OR 
                    ((tmsd.scheduled_date <= "{end_date}") AND (tmsd.scheduled_date >= "{start_date}") AND tmsd.docstatus = 1)
                OR 
                    ((tmsd.scheduled_date <= "{start_date}" AND tmsd.custom_scheduled_end_date >= "{end_date}") AND tmsd.docstatus = 1) ORDER BY parent;
            ''', as_dict = 1)
            
            if len(sales_persons) > 0:
                for sp in sales_persons:
                    if sp.sales_person == schedule.sales_person:
                        frappe.throw("Sales person {0} is not available between {1} to {2}".format(frappe.bold(schedule.sales_person), start_date, end_date))