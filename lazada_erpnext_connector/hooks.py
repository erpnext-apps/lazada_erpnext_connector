# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "lazada_erpnext_connector"
app_title = "Lazada ERPNext Connector"
app_publisher = "Raaj Tailor"
app_description = "Lazada Ecommerce Platform Integration witH E"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "tailorraj111@gmail.com"
app_license = "MIT"

fixtures = ["Custom Field"]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lazada_erpnext_connector/css/lazada_erpnext_connector.css"
# app_include_js = "/assets/lazada_erpnext_connector/js/lazada_erpnext_connector.js"
app_include_js = ["/assets/lazada_erpnext_connector/js/lazada.js"]

# include js, css files in header of web template
# web_include_css = "/assets/lazada_erpnext_connector/css/lazada_erpnext_connector.css"
# web_include_js = "/assets/lazada_erpnext_connector/js/lazada_erpnext_connector.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}
doctype_js = {
    "Sales Order": ["custom_scripts/sales_order.js"],
}
# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "lazada_erpnext_connector.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "lazada_erpnext_connector.install.before_install"
# after_install = "lazada_erpnext_connector.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lazada_erpnext_connector.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
	
	"Delivery Note" :{
		"on_submit": "lazada_erpnext_connector.lazada_erpnext_connector.delivery_note.submit",
    "validate": "lazada_erpnext_connector.lazada_erpnext_connector.delivery_note.validate",
	
}
 ,
   "Stock Entry":{
     "on_submit":"lazada_erpnext_connector.lazada_erpnext_connector.stock_entry.submit"
   }
  }
# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "cron": {
    #     "*/1 * * * *":[
    #     "lazada_erpnext_connector.lazada_erpnext_connector.doctype.lazada_settings.lazada_settings.get_refresh"
    # ]
    # }
    "daily": [
		"lazada_erpnext_connector.lazada_erpnext_connector.doctype.lazada_settings.lazada_settings.get_refresh"
	],
  "hourly": [
		"lazada_erpnext_connector.lazada_erpnext_connector.doctype.lazada_settings.lazada_settings.get_orders"
	]
    
}

# scheduler_events = {
# 	"all": [
# 		"lazada_erpnext_connector.tasks.all"
# 	],
# 	"daily": [
# 		"lazada_erpnext_connector.tasks.daily"
# 	],
# 	"hourly": [
# 		"lazada_erpnext_connector.tasks.hourly"
# 	],
# 	"weekly": [
# 		"lazada_erpnext_connector.tasks.weekly"
# 	]
# 	"monthly": [
# 		"lazada_erpnext_connector.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "lazada_erpnext_connector.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "lazada_erpnext_connector.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lazada_erpnext_connector.task.get_dashboard_data"
# }

