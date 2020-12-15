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
    # frappe.msgprint("in_submit")
    if self.update_on_lazada == 1:
        # frappe.msgprint("here")
        lazada_warehouse = frappe.db.get_value("Lazada Defaults",None,"default_warehouse")
        for item in self.items:
            if item.t_warehouse == lazada_warehouse:
                new_stock = frappe.get_value("Bin",{"warehouse":lazada_warehouse,"item_code":item.item_code},"actual_qty")
                # frappe.msgprint(str(new_stock))
                set_stock_lazada(item.item_code,int(new_stock))
        #     item_ids.append(item.order_item_id)
        
        # # response = client.execute(request, frappe.db.get_value("Lazada Settings",None,"access_token"))
        # frappe.msgprint(str(response.body))
def set_stock_lazada(sku_id,qty):
    client = LazopClient(frappe.db.get_value("Lazada Settings",None,"url"), frappe.db.get_value("Lazada Settings",None,"api_key") ,api_secret)
    request = LazopRequest('/product/price_quantity/update')
    request.add_api_param('payload', """<Request>
                                            <Product>
                                                <Skus>
                                                <Sku>
                                                    <SellerSku>{sku}</SellerSku>        
                                                    <Quantity>{qty}</Quantity>
                                                </Sku>
                                                </Skus>
                                            </Product>
                                        </Request>""".format(sku=sku_id,qty=qty))
    response = client.execute(request, access_token)
    if str(response.body['code']) == '0':
        frappe.msgprint("Stock has been updated to Lazada Seller!")
    else:
        # create_error_log('/order/rts',response.code,response.message)
        frappe.throw("Error Occured While updating Stock on Lazada. Error: {}".format(response.message))
        # frappe.throw("Can't find Order with order id {}".format(self.lazada_order_id))
    
def create_error_log(call,error_code,error):
    doc = frappe.new_doc("Lazada Connector Error Log")
    doc.call=call
    doc.error_code=error_code
    doc.error_log=error
    doc.insert(ignore_permissions=True)

