# -*- coding: utf-8 -*-
'''
Created on 2018-03-21

@author: xuteng.xt
'''

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

# dir = os.getenv('HOME')
dir = expanduser("~")
isExists = os.path.exists(dir + "/logs")
if not isExists:
    os.makedirs(dir + "/logs") 
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.ERROR)
handler = logging.FileHandler(dir + "/logs/lazopsdk.log." + time.strftime("%Y-%m-%d", time.localtime()))
handler.setLevel(logging.ERROR)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

P_SDK_VERSION = "lazop-sdk-python-20181207"

P_APPKEY = "app_key"
P_ACCESS_TOKEN = "access_token"
P_TIMESTAMP = "timestamp"
P_SIGN = "sign"
P_SIGN_METHOD = "sign_method"
P_PARTNER_ID = "partner_id"
P_DEBUG = "debug"

P_CODE = 'code'
P_TYPE = 'type'
P_MESSAGE = 'message'
P_REQUEST_ID = 'request_id'

P_API_GATEWAY_URL_SG = 'https://api.lazada.sg/rest'
P_API_GATEWAY_URL_MY = 'https://api.lazada.com.my/rest'
P_API_GATEWAY_URL_VN = 'https://api.lazada.vn/rest'
P_API_GATEWAY_URL_TH = 'https://api.lazada.co.th/rest'
P_API_GATEWAY_URL_PH = 'https://api.lazada.com.ph/rest'
P_API_GATEWAY_URL_ID = 'https://api.lazada.co.id/rest'
P_API_AUTHORIZATION_URL = 'https://auth.lazada.com/rest'

P_LOG_LEVEL_DEBUG = "DEBUG"
P_LOG_LEVEL_INFO = "INFO"
P_LOG_LEVEL_ERROR = "ERROR"


def sign(secret,api, parameters):
    #===========================================================================
    # @param secret
    # @param parameters
    #===========================================================================
    sort_dict = sorted(parameters)
    
    parameters_str = "%s%s" % (api,
        str().join('%s%s' % (key, parameters[key]) for key in sort_dict))

    h = hmac.new(secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"), digestmod=hashlib.sha256)

    return h.hexdigest().upper()


def mixStr(pstr):
    if(isinstance(pstr, str)):
        return pstr
    elif(isinstance(pstr, unicode)):
        return pstr.encode('utf-8')
    else:
        return str(pstr)

def logApiError(appkey, sdkVersion, requestUrl, code, message):
    localIp = socket.gethostbyname(socket.gethostname())
    platformType = platform.platform()
    logger.error("%s^_^%s^_^%s^_^%s^_^%s^_^%s^_^%s^_^%s" % (
        appkey, sdkVersion,
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        localIp, platformType, requestUrl, code, message))

class LazopRequest(object):
    def __init__(self,api_pame,http_method = 'POST'):
        self._api_params = {}
        self._file_params = {}
        self._api_pame = api_pame
        self._http_method = http_method

    def add_api_param(self,key,value):
        self._api_params[key] = value

    def add_file_param(self,key,value):
        self._file_params[key] = value


class LazopResponse(object):
    def __init__(self):
        self.type = None
        self.code = None
        self.message = None
        self.request_id = None
        self.body = None
    
    def __str__(self, *args, **kwargs):
        sb = "type=" + mixStr(self.type) +\
            " code=" + mixStr(self.code) +\
            " message=" + mixStr(self.message) +\
            " requestId=" + mixStr(self.request_id)
        return sb

class LazopClient(object):
    
    log_level = P_LOG_LEVEL_ERROR
    def __init__(self, server_url,app_key,app_secret,timeout=30):
        self._server_url = server_url
        self._app_key = app_key
        self._app_secret = app_secret
        self._timeout = timeout
    
    def execute(self, request,access_token = None):

        sys_parameters = {
            P_APPKEY: self._app_key,
            P_SIGN_METHOD: "sha256",
            P_TIMESTAMP: str(int(round(time.time()))) + '000',
            P_PARTNER_ID: P_SDK_VERSION
        }

        if(self.log_level == P_LOG_LEVEL_DEBUG):
            sys_parameters[P_DEBUG] = 'true'

        if(access_token):
            sys_parameters[P_ACCESS_TOKEN] = access_token

        application_parameter = request._api_params;

        sign_parameter = sys_parameters.copy()
        sign_parameter.update(application_parameter)

        sign_parameter[P_SIGN] = sign(self._app_secret,request._api_pame,sign_parameter)

        api_url = "%s%s" % (self._server_url,request._api_pame)

        full_url = api_url + "?";
        for key in sign_parameter:
            full_url += key + "=" + str(sign_parameter[key]) + "&";
        full_url = full_url[0:-1]

        try:
            if(request._http_method == 'POST' or len(request._file_params) != 0) :
                r = requests.post(api_url,sign_parameter,files=request._file_params, timeout=self._timeout)
            else:
                r = requests.get(api_url,sign_parameter, timeout=self._timeout)
        except Exception as err:
            logApiError(self._app_key, P_SDK_VERSION, full_url, "HTTP_ERROR", str(err))
            raise err

        response = LazopResponse()

        jsonobj = r.json()

        if P_CODE in jsonobj:
            response.code = jsonobj[P_CODE]
        if P_TYPE in jsonobj:
            response.type = jsonobj[P_TYPE]
        if P_MESSAGE in jsonobj:
            response.message = jsonobj[P_MESSAGE]
        if P_REQUEST_ID in jsonobj:
            response.request_id = jsonobj[P_REQUEST_ID]

        if response.code is not None and response.code != "0":
            logApiError(self._app_key, P_SDK_VERSION, full_url, response.code, response.message)
        else:
            if(self.log_level == P_LOG_LEVEL_DEBUG or self.log_level == P_LOG_LEVEL_INFO):
                logApiError(self._app_key, P_SDK_VERSION, full_url, "", "")

        response.body = jsonobj

        return response
