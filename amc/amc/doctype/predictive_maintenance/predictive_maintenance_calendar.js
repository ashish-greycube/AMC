frappe.views.calendar["Predictive Maintenance"] = {
	field_map: {
		start: "scheduled_date",
		end: "scheduled_end_date",
		id: "name",
		title: "subject",
        tooltip: "subject",	
		allDay: "allDay",
	},
	gantt: true,
    get_events_method: "frappe.desk.calendar.get_events",
};