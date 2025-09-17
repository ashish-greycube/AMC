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
            sd_doc.description = schedule.custom_remark or ""
            sd_doc.contact_person = self.contact_person
            sd_doc.mobile_no = self.contact_mobile
            sd_doc.contact_email = self.contact_email
            sd_doc.sales_order_reference = self.sales_order_cf
            sd_doc.maintenance_schedule_reference = self.name
            sd_doc.sales_person_email = schedule.custom_sales_person_email
            sd_doc.qty = schedule.qty
            sd_doc.maintenance_schedule_item_reference = schedule.name
            sd_doc.insert(ignore_permissions=True)
        
            # frappe.db.set_value('Maintenance Schedule Detail', schedule.name, 'custom_amc_schedule_reference', sd_doc.name)
            schedule_doc = frappe.get_doc('Maintenance Schedule Detail', schedule.name)
            schedule_doc.custom_amc_schedule_reference = sd_doc.name
            schedule_doc.save(ignore_permissions=True)

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
    
    # Set Sales Person Email
    if len(self.schedules) > 0:
        for row in self.schedules:
            sp = row.sales_person
            employee_id = frappe.db.get_value('Sales Person', sp, 'employee')
            sp_email = ""
            if employee_id != None:
                sp_email = frappe.db.get_value('Employee', employee_id, 'prefered_email')
            row.custom_sales_person_email = sp_email
    
    if len(self.schedules) > 0:
        email = self.schedules[0].custom_sales_person_email
        self.custom_sp_email = email


@frappe.whitelist()
def update_predictive_data_after_submit(doctype, docname, predictive_doc, reschedule_reason, updated_schedule_date, updated_scheduled_end_date,  item_code, branch, parent, idx):
    # Validating Dates:
    maintenance_doc = frappe.get_doc("Maintenance Schedule", parent)
    for item in maintenance_doc.items:
        if item.name == idx:
            current_ms_item = item

    if frappe.utils.getdate(updated_schedule_date) < current_ms_item.start_date or frappe.utils.getdate(updated_schedule_date) > current_ms_item.end_date:
        frappe.throw("Schedule start date is beyond the assigned quarter for item {0}".format(item_code))

    if frappe.utils.getdate(updated_scheduled_end_date) > current_ms_item.end_date or frappe.utils.getdate(updated_scheduled_end_date) < current_ms_item.start_date:
        frappe.throw("Schedule end date is beyond the assigned quarter for item {0}".format(item_code))

    
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
    
    if current_allowed_occurance == None:
        frappe.throw("Occurance value is not set in Item {0}".format(frappe.bold(item_code)))
    elif current_total_pairs >= current_allowed_occurance:
        frappe.throw("Simultaneous Occurrence for Item {0} Exceeds Permitted Occurence {1}".format(frappe.bold(item_code), current_allowed_occurance))
    else:
        # Updating Child Table Data
        frappe.db.set_value(doctype, docname, 'scheduled_date', updated_schedule_date)
        frappe.db.set_value(doctype, docname, 'custom_scheduled_end_date', updated_scheduled_end_date)
        frappe.db.set_value(doctype, docname, 'custom_reschedule_reason', reschedule_reason)

        # Updating Predictive Maintenance Data
        frappe.db.set_value('Predictive Maintenance', predictive_doc, 'scheduled_date', updated_schedule_date)
        frappe.db.set_value('Predictive Maintenance', predictive_doc, 'scheduled_end_date', updated_scheduled_end_date)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_contact_person_query(doctype, txt, searchfield, start, page_len, filters):
    data = frappe.db.sql(
        '''
    	SELECT tdl.parent 
        FROM tabCustomer tc
        INNER JOIN `tabDynamic Link` tdl 
        ON tc.name = tdl.link_name 
        WHERE tdl.link_doctype  = "Customer" 
        AND tdl.parenttype = "Contact"
        AND tc.name = "{0}"
        AND tdl.parent like %(txt)s
        '''.format(filters.get('customer')), {"txt": "%%%s%%" % txt}
    )
    return data

@frappe.whitelist()
def update_contact_in_pm(parent, new_contact_person, new_contact_phone, new_contact_email):
    # Updating Details in MS
    frappe.db.set_value('Maintenance Schedule', parent, 'contact_person', new_contact_person)
    frappe.db.set_value('Maintenance Schedule', parent, 'contact_mobile', new_contact_phone)
    frappe.db.set_value('Maintenance Schedule', parent, 'contact_email', new_contact_email)

    # Updating Details in PM
    predictive_docs = frappe.db.get_all('Predictive Maintenance', {'maintenance_schedule_reference' : parent}, ['name'])
    if len(predictive_docs) > 0:
        for pd in predictive_docs:
            docname = pd['name']
            frappe.db.set_value('Predictive Maintenance', docname, 'contact_person', new_contact_person)
            frappe.db.set_value('Predictive Maintenance', docname, 'mobile_no', new_contact_phone)
            frappe.db.set_value('Predictive Maintenance', docname, 'contact_email', new_contact_email)

#Final Changes---------------------------------------------
def validate_dates_of_schedule_table(self, method=None):
    item_table = self.items
    schedule_table = self.schedules
    if len(schedule_table) > 0:
        for item in item_table:
            item_name = item.item_code
            start = item.start_date
            end = item.end_date

            for scitem in schedule_table:
                scitem_name = scitem.item_code
                scstart_date = scitem.scheduled_date
                scend_date = scitem.custom_scheduled_end_date
                if scstart_date != None and scend_date != None:
                    if item_name == scitem_name and item.idx == scitem.idx:
                        if scstart_date < start or scstart_date > end:
                            frappe.throw("Schedule start date is beyond the assigned quarter for item {0}".format(scitem_name))

                        if scend_date > end or scend_date < start:
                            frappe.throw("Schedule end date is beyond the assigned quarter for item {0}".format(scitem_name))

def update_status_on_submit_of_mv(self, method=None):
    status = self.completion_status
    print()
    schedule_item_reference = self.purposes[0].maintenance_schedule_detail
    predictive_doc = frappe.get_doc("Predictive Maintenance", {'maintenance_schedule_item_reference': schedule_item_reference})
    print(predictive_doc.name)
    if predictive_doc != None:
        # frappe.db.set_value("Predictive Maintenance", predictive_doc, 'completion_status', status)
        predictive_doc.completion_status = status
        # Set Color For Calendar View
        if status == "Partially Completed":
            predictive_doc.color = '#fff200'
            # frappe.db.set_value("Predictive Maintenance", predictive_doc.name, 'color', '#fff200')
        elif status == "Fully Completed":
            predictive_doc.color = '#29CD42'
            # frappe.db.set_value("Predictive Maintenance", predictive_doc.name, 'color', '#29CD42')
        else:
            predictive_doc.color = '#449CF0'
            # frappe.db.set_value("Predictive Maintenance", predictive_doc.name, 'color', '#449CF0')
        predictive_doc.save()

def update_status_on_cancel_of_mv(self, method=None):
    status = "Pending"
    schedule_item_reference = self.purposes[0].maintenance_schedule_detail
    predictive_doc = frappe.get_doc("Predictive Maintenance", {'maintenance_schedule_item_reference': schedule_item_reference})
    if predictive_doc != None:
        predictive_doc.completion_status = status
        predictive_doc.color = '#449CF0'
        predictive_doc.save()