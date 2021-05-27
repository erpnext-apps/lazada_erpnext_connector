from __future__ import unicode_literals
import frappe
from lazada_erpnext_connector.lazada_erpnext_connector.doctype.lazada_settings.lazada_settings import LazopClient,LazopRequest


def get_pw(doctype,field_name):
    docSettings = frappe.get_single(doctype)
    strPassword = docSettings.get_password(field_name)
    return strPassword

api_secret = get_pw("Lazada Settings","api_secret")
access_token = get_pw("Lazada Settings","access_token")

def submit(self,method):
    if self.update_lazada_status:
        item_ids = []
        for item in self.items:
            item_ids.append(item.order_item_id)
        client = LazopClient(frappe.db.get_value("Lazada Settings",None,"url"), frappe.db.get_value("Lazada Settings",None,"api_key") ,api_secret)
        request = LazopRequest('/order/rts')
        request.add_api_param('delivery_type', 'dropship')
        request.add_api_param('order_item_ids', str(item_ids))
        request.add_api_param('shipment_provider', self.shipment_provider)
        request.add_api_param('tracking_number', '12345678')
        response = client.execute(request, access_token)
        # response = client.execute(request, frappe.db.get_value("Lazada Settings",None,"access_token"))
        if response.code == '0':
            frappe.msgprint("Sales Order is Ready to Ship!")
        else:
            create_error_log('/order/rts',response.code,response.message)
            frappe.msgprint("Error Occured While updating status on Lazada. Please Check Lazada Connector Error Log")
        frappe.msgprint(str(response.body))
def validate(self,method):
    if self.update_lazada_status:
        request = LazopRequest('/order/get','GET')
        request.add_api_param('order_id', str(self.lazada_order_id))
        client = LazopClient(frappe.db.get_value("Lazada Settings",None,"url"), frappe.db.get_value("Lazada Settings",None,"api_key") ,api_secret)
        response = client.execute(request, access_token)
        # frappe.msgprint(str(response))
        if str(response.body['code']) == '0':
            # frappe.msgprint(str(response.body['data']['statuses']))
            if "canceled" in list(response.body['data']['statuses']):
                frappe.throw("This Sales Order id Cancelled in Lazada Seller!")
        else:
            # create_error_log('/order/rts',response.code,response.message)
            frappe.throw("Error Occured While creating Delivery Note. Error: {}".format(response.message))
            # frappe.throw("Can't find Order with order id {}".format(self.lazada_order_id))
    
def create_error_log(call,error_code,error):
    doc = frappe.new_doc("Lazada Connector Error Log")
    doc.call=call
    doc.error_code=error_code
    doc.error_log=error
    doc.insert(ignore_permissions=True)
