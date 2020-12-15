# -*- coding: utf-8 -*-
# Copyright (c) 2020, Raaj Tailor and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import time
import hmac
import hashlib
import json
import mimetypes
import itertools
import random
import logging
import os
from os.path import expanduser
import socket
import platform
from datetime import datetime
from frappe.utils import now,getdate,add_days
from frappe import enqueue
from lazada_erpnext_connector.utils.lazada_utils import LazopClient,LazopRequest,LazopResponse


class LazadaSettings(Document):

    def get_access_token(self):
        auth = Authentication()
        auth.get_access_token()
    def get_refresh_token(self):
        auth = Authentication()
        auth.get_refresh_token()
    def get_products(self):
        prod = Products()
        prod.create_erpnext_items()
    def get_orders(self):
        ord = Orders()
        ord.create_erpnext_order()
    def get_transactions(self):
        trans = Transaction()
        trans.create_erpnext_jornal_entry()
    def get_shippment_pro(self):
        ship_pro = Delivery()
        frappe.msgprint(str(ship_pro.get_shippment_provider()))

# *****************************************************************************************************************
# Defaults Global Variables
# *****************************************************************************************************************

def get_pw(doctype,field_name):
    docSettings = frappe.get_single(doctype)
    strPassword = docSettings.get_password(field_name)
    return strPassword

api_key = frappe.db.get_value("Lazada Settings",None,"api_key")
api_secret = get_pw("Lazada Settings","api_secret")
access_token = get_pw("Lazada Settings","access_token")
url = frappe.db.get_value("Lazada Settings",None,"url")
# *****************************************************************************************************************
# API Functions Classes
# *****************************************************************************************************************

class Products(LazadaSettings):
    def __init__(self):
        
        self.last_sync_prod = frappe.db.get_value("Lazada Settings",None,"product_last_sync")
        self.sync_limit = frappe.db.get_value("Lazada Settings",None,"sync_limit")
        self.synced_items = frappe.db.get_value("Lazada Settings",None,"synced_items")
        self.created_after = frappe.db.get_value("Lazada Settings",None,"created_after")
        self.search_item = frappe.db.get_value("Lazada Settings",None,"search_item")

    def get_all_products(self,limit,offset):
        client = LazopClient(url, api_key ,api_secret)
        request = LazopRequest('/products/get','GET')
        request.add_api_param('filter', 'all')
        request.add_api_param('offset', offset)
        request.add_api_param('limit', limit)

        if self.search_item:
            sku_list = json.dumps(self.search_item.split(","))
            frappe.msgprint(str(sku_list))
            request.add_api_param('sku_seller_list', sku_list)
        
        if self.created_after:
            created_after = datetime.strptime(str(self.created_after),"%Y-%m-%d").isoformat()
            request.add_api_param('create_after', created_after)
        
        response = client.execute(request, access_token)
        if response.code != '0':
            # frappe.msgprint("Call is not sucessful")
            create_error_log('/products/get',response.code,response.message)
            frappe.msgprint("There is some error while creating Items. Please Check Lazada Error Log!")
            return False
        else:
            # frappe.msgprint(str(response.code))
            # frappe.msgprint(str(response.body))
            if bool(response.body['data']):
                return (response.body['data']['total_products'],response.body)
            else:
                frappe.msgprint("No Item Found to Sync!")
                frappe.db.set_value("Lazada Settings",None,"synced_items",0)
                return False

            # frappe.msgprint(str(bool(response.body['data'])))
           
    
  

    def create_erpnext_items(self):
        lazada_product = self.get_all_products(self.sync_limit,self.synced_items)
        # frappe.throw(str(lazada_product))
        if lazada_product:
            # frappe.db.set_value("Lazada Settings",None,"total_lazada_item",int(lazada_product[0]))
            products = lazada_product[1]

            if products and products['data']:
                count = 0
                for product in products['data']['products']:
                    for sku in product['skus']:
                        count = count + 1
                        if not frappe.db.exists("Item", sku['SellerSku']):
                            if not frappe.db.exists("Item Group", product['primary_category']):
                                item_group = frappe.new_doc("Item Group")
                                item_group.item_group_name = str(product['primary_category'])
                                item_group.is_group = 0
                                item_group.parent_item_group = "Lazada Item Category"
                                item_group.insert(ignore_permissions=True)

                            item_doc = frappe.new_doc("Item")
                            item_doc.item_code = str(sku['SellerSku'])
                            item_doc.item_name = product['attributes']['name']
                            if 'short_description' in (product['attributes'].keys()):
                                item_doc.description = product['attributes']['short_description']
                            item_doc.item_group = product['primary_category']
                            item_doc.stock_uom = "Nos"
                            item_doc.is_stock_item = 1
                            item_doc.valuation_rate = 1
                            item_doc.opening_stock = sku['quantity']
                            item_doc.insert(ignore_permissions=True)
                            item_doc.item_defaults = [{
                                "company":frappe.db.get_value("Global Defaults",None,"default_company"),
                                "default_warehouse":frappe.db.get_value("Lazada Defaults",None,"default_warehouse")
                            }]
                            frappe.msgprint(str(item_doc.name)+" Created!")
                            frappe.db.set_value("Lazada Settings",None,"product_last_sync",datetime.now().replace(microsecond=0).isoformat())
                        
                        else:
                            frappe.msgprint("Item {} is already created".format(sku['SellerSku']))
                frappe.db.set_value("Lazada Settings",None,"synced_items",int(frappe.db.get_value("Lazada Settings",None,"synced_items")) + count)
                # frappe.db.set_value("Lazada Settings",None,"remaining_items",int(frappe.db.get_value("Lazada Settings",None,"total_lazada_item")) -int(frappe.db.get_value("Lazada Settings",None,"synced_items")))
                
        # else:
        #     frappe.msgprint("There is some error while creating Items. Please Check Lazada Error Log!")

class Delivery(object):
    def __init__(self):
        pass
    def get_shippment_provider(self):
        client = LazopClient(url, api_key ,api_secret)
        request = LazopRequest('/shipment/providers/get','GET')

        response = client.execute(request, access_token)
        data = response.body['data']['shipment_providers']
        for ship in data:
            shipment_provider = {
                "doctype":"Shipment Provider",
                "shipment_provider":ship['name'],
                "is_cod":ship['cod']
            }
            if not frappe.db.exists("Shipment Provider", ship['name']):
                frappe.get_doc(shipment_provider).insert(ignore_permissions=True)
        frappe.db.set_value("Lazada Settings",None,"last_shipment_provider_sync",datetime.now().replace(microsecond=0).isoformat())
        return response.body
        # print(response.type)
        # print(response.body)                 

class Orders(object):
    def __init__(self):
        
        self.default_customer = frappe.db.get_value("Lazada Defaults",None,"customer")
        self.default_warehouse = frappe.db.get_value("Lazada Defaults",None,"default_warehouse")
        self.last_sync = frappe.db.get_value("Lazada Settings",None,"order_last_sync")

    def get_all_orders(self):
        client = LazopClient(url, api_key ,api_secret)
        request = LazopRequest('/orders/get','GET')
        request.add_api_param('created_after', self.last_sync)
        request.add_api_param('status', 'pending')
        request.add_api_param('limit', 50)
        request.add_api_param('sort_direction', 'DESC')
        # frappe.msgprint(str(access_token))
        response = client.execute(request,access_token)
        # frappe.msgprint(str(response.type))
        # frappe.msgprint(str(response.body))
        if response.code != '0':
            # frappe.msgprint("Call is not sucessful")
            create_error_log('/orders/get',response.code,response.message)
            return False
        else:
            # frappe.msgprint(str(response.code))
            # frappe.msgprint(str(response.body))
            return response.body
        
    
    def get_order_items(self,order_id):
        client = LazopClient(url, api_key ,api_secret)
        request = LazopRequest('/orders/items/get','GET')
        request.add_api_param('order_ids', order_id)
        response = client.execute(request, access_token)
        if response.code != '0':
            # frappe.msgprint("Call is not sucessful")
            create_error_log('/orders/items/get',response.code,response.message)
            return False
        else:
            # frappe.msgprint(str(response.code))
            # frappe.msgprint(str(response))
            # res_body = response.body
            return response.body
        # return response.body


    
    def create_erpnext_order(self):
        orders_list = self.get_all_orders()
        orders_ids=[]
        if orders_list:
            for order in orders_list['data']['orders']:
                orders_ids.append(str(order['order_id']))
            order_items = self.get_order_items(str(orders_ids))
            if order_items:
                for order in orders_list['data']['orders']:
                    for order_item in order_items['data']:
                        if order['order_id'] == order_item['order_id']:
                            items = []
                            for item in order_item['order_items']:
                                items.append({
                                    "item_code":item['sku'],
                                    "item_name":item["name"],
                                    "rate":item['item_price'],
                                    "qty":1,
                                    "order_item_id":item['order_item_id']
                                })
                            sales_order = {
                            "doctype":"Sales Order",
                            "customer":self.default_customer,
                            "set_warehouse":self.default_warehouse,
                            "transaction_date":getdate(datetime.strptime(order['created_at'], "%Y-%m-%d %H:%M:%S %z")),
                            "delivery_date":add_days(getdate(datetime.strptime(order['created_at'], "%Y-%m-%d %H:%M:%S %z")),2),
                            "lazada_order_id":order['order_id'],
                            "po_no":order['order_number'],
                            "items":items,
                            "cash_direct_sales_name":order['address_billing']['first_name'],
                            "order_type":"Sales"}
                            if not frappe.db.exists("Sales Order", frappe.db.get_value("Sales Order",{"po_no":order['order_number']},"name")):
                                # frappe.msgprint(str(items))
                                # frappe.msgprint(str(sales_order))
                                res_doc = frappe.get_doc(sales_order).insert(ignore_permissions=True)
                                frappe.msgprint("Sales Order Created {}".format(res_doc.name))
                
            frappe.db.set_value("Lazada Settings",None,"order_last_sync",datetime.now().replace(microsecond=0).isoformat())

class OrdersDoc(object):
    def __init__(self):
        pass

    def get_oreder_doc(self,order_item_ids):
        client = LazopClient(url, api_key ,api_secret)
        request = LazopRequest('/order/document/get','GET')
        request.add_api_param('doc_type', 'invoice')
        request.add_api_param('order_item_ids', order_item_ids)
        
        response = client.execute(request, access_token)
        # frappe.msgprint(str(response.type))
        # frappe.msgprint(str(response.body))
        return response.body
    
    def attach_to_erpnext_invoice(self):
        pass
        
class Transaction(object):
    def __init__(self):
        
        self.company = frappe.db.get_value("Global Defaults",None,"default_company")
        self.cash_account = frappe.db.get_value("Company",self.company,"default_cash_account")
        self.receivalble = frappe.db.get_value("Company",self.company,"default_receivable_account")
        self.customer = frappe.db.get_value("Lazada Defaults",None,"customer")
        self.last_transc_sync = frappe.db.get_value("Lazada Defaults",None,"transaction_last_sync")
        self.from_date = frappe.db.get_value("Lazada Settings",None,"from_date")
        self.to_date = frappe.db.get_value("Lazada Settings",None,"to_date")

    def get_all_transaction(self):
        # frappe.msgprint(str(self.from_date))
        # frappe.throw(str(self.to_date))
        if not self.from_date or not self.to_date:
            frappe.throw("Please Enter <b>From Date</b> and <b>To Date</b> to get Transaction.")
        client = LazopClient(url, api_key ,api_secret)
        request = LazopRequest('/finance/transaction/detail/get','GET')
        request.add_api_param('trans_type', '13')
        request.add_api_param('end_time', str(self.to_date))
        request.add_api_param('start_time',str(self.from_date))
        response = client.execute(request, access_token)
        # frappe.msgprint(str(response.type))
        # frappe.msgprint(str(response.body))
        return response.body
    
    def create_erpnext_jornal_entry(self):
        transaction_list = self.get_all_transaction()
        account_entry = []
        invoice_list = []

        for transc in transaction_list['data']:
            sales_invoice = frappe.db.get_value("Sales Invoice",{"po_no":transc["order_no"],"je_created":0},"name")
            if sales_invoice:
                account_entry.append({
                    "account":self.receivalble,
                    "party_type":"Customer",
                    "party":self.customer,
                    "credit_in_account_currency":float(transc['amount']),
                    "reference_type":"Sales Invoice",
                    "reference_name":sales_invoice
                })
                account_entry.append({
                    "account":self.cash_account,
                    "debit_in_account_currency":float(transc['amount']),
                    
                })
                invoice_list.append(sales_invoice)
        
        if len(account_entry) != 0:
            frappe.msgprint(str(account_entry))
            self.creat_je(account_entry,invoice_list)
        frappe.db.set_value("Lazada Settings",None,"transaction_last_sync",datetime.now().replace(microsecond=0).isoformat())
    
    def creat_je(self,account_entry,invoice_list):
        je_doc ={
            "doctype":"Journal Entry",
            "voucher_type":"Journal Entry",
            "posting_date":frappe.utils.now(),
            "accounts":account_entry
        }
        frappe.get_doc(je_doc).insert(ignore_permissions=True)

        for inv in invoice_list:
            frappe.db.set_value("Sales Invoice",inv,"je_created",1)
            frappe.msgprint("Payment Created For Invoice {}".format(inv))
        
class Authentication(object):
    def __init__(self):
        self.callback_url = frappe.db.get_value("Lazada Settings",None,"callback_url")
        self.refresh_token = get_pw("Lazada Settings","refresh_token")
        
    def get_code(self):
        res = frappe.db.get_value("Lazada Settings",None,"code")
        # res = requests.get("https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri={call_back_url}&client_id={appkey}".format(call_back_url=self.callback_url,appkey=self.api_key))
        # frappe.msgprint(str(res))
        return res

    def get_access_token(self):
        client = LazopClient("https://auth.lazada.com/rest", api_key ,api_secret)
        request = LazopRequest('/auth/token/create')
        request.add_api_param("code", self.get_code())
        response = client.execute(request)
        # frappe.msgprint(str(response.body))
        if response.body['code'] != '0':
            frappe.msgprint("Access token is Already Generated. Please Use Refresh Token Button!")
        else:
            frappe.db.set_value("Lazada Settings",None,"access_token",response.body["access_token"])
            frappe.db.set_value("Lazada Settings",None,"refresh_token",response.body['refresh_token'])
            frappe.msgprint("Access Token has been successfully Genrated. Please Reload Page.")
        
    def get_refresh_token(self):
        client = LazopClient("https://auth.lazada.com/rest", api_key ,api_secret)
        request = LazopRequest('/auth/token/refresh')
        request.add_api_param("refresh_token", self.refresh_token)
        response = client.execute(request)
        # frappe.msgprint(str(response.body))
        # frappe.msgprint(str(now()))
        if response.body['code'] == '0':
            frappe.db.set_value("Lazada Settings",None,"access_token",response.body["access_token"])
            frappe.db.set_value("Lazada Settings",None,"refresh_token",response.body['refresh_token'])
            frappe.db.set_value("Lazada Settings",None,"last_sync_access_token",now())
            frappe.msgprint("Access Token has been refreshed successfully. Please Reload Page!")
        else:
            frappe.msgprint("Error Occured While Refreshing Acces token.")

# *********************************************************************************************************************
# FunctionS called By Scheduler
# *********************************************************************************************************************

def create_error_log(call,error_code,error):
    doc = frappe.new_doc("Lazada Connector Error Log")
    doc.call=call
    doc.error_code=error_code
    doc.error_log=error
    doc.insert(ignore_permissions=True)

frappe.whitelist()
def get_refresh():
    auth = Authentication()
    auth.get_refresh_token()

frappe.whitelist()
def get_orders():
    ord = Orders()
    ord.create_erpnext_order()

frappe.whitelist()
def get_items_back():
    prod = Products()
    prod.create_erpnext_items()



