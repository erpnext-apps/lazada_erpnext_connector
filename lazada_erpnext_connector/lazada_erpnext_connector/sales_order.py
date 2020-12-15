from __future__ import unicode_literals
import frappe
from lazada_erpnext_connector.lazada_erpnext_connector.doctype.lazada_settings.lazada_settings import LazopClient,LazopRequest

def submit(self,method):
    item_ids = []
    for item in self.items:
        item_ids.append(item.order_item_id)
    client = LazopClient(frappe.db.get_value("Lazada Settings",None,"url"), frappe.db.get_value("Lazada Settings",None,"api_key") ,frappe.db.get_value("Lazada Settings",None,"api_secret"))
    request = LazopRequest('/order/rts')
    request.add_api_param('delivery_type', 'dropship')
    request.add_api_param('order_item_ids', str(item_ids))
    request.add_api_param('shipment_provider', self.shipment_provider)
    request.add_api_param('tracking_number', '12345678')
    response = client.execute(request, frappe.db.get_value("Lazada Settings",None,"access_token"))
    # response = client.execute(request, frappe.db.get_value("Lazada Settings",None,"access_token"))
    frappe.msgprint(str(response.body))
    
