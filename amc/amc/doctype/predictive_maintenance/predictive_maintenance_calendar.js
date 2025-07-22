frappe.views.calendar["Predictive Maintenance"] = {
	field_map: {
		start: "scheduled_date",
		end: "scheduled_end_date",
		id: "name",
		title: "subject",
        tooltip: "subject",	
		allDay: "allDay",
		color: "color",
	},
    get_css_class: function (data) {
        console.log(data)
        if (data.color === "#fff200") {
            return "yellow";
        }
        if (data.color === "#29CD42") {
            return "green";
        }
        if (data.color === "#449CF0") {
            return "blue";
        }
    },
	gantt: true,
    get_events_method: "frappe.desk.calendar.get_events",
};