# -*- coding: utf-8 -*-

#from platinumegg.lib.platform.api.request import ApiRequestMakerBase
from platinumegg.lib.platform.api.request import ApiRequestMakerBase, ApiRequest
from platinumegg.lib.platform.api.objects import People, PaymentData,\
    PaymentItem, PaymentPostResultData, InspectionData, IgnorelistData
from platinumegg.lib.pljson import Json


URL_API_DEV = 'http://sbx-osapi.dmm.com/social_pc/rest'
CERTIFICATE_DEV = """-----BEGIN CERTIFICATE-----
MIICBjCCAW+gAwIBAgIJAPsTZEAzBoecMA0GCSqGSIb3DQEBBQUAMBwxGjAYBgNV
BAMMEXNieC1vc2FwaS5kbW0uY29tMB4XDTE2MDUxMDAwMjIxM1oXDTE4MDUxMDAw
MjIxM1owHDEaMBgGA1UEAwwRc2J4LW9zYXBpLmRtbS5jb20wgZ8wDQYJKoZIhvcN
AQEBBQADgY0AMIGJAoGBAM0flQl+Mkek4IkvQfCoy8mJ5gxV8WIPYPKebU5eyfSY
O1jnPqAi5HRl3747Z/Hoey1a9oUjFiYav0LyjoadnJtQAzj3Ma7LULDmEMJtkPvo
MJZXXELfUYjabwpEqO2/twzLBv2Ho2UD5dosF1+hIHofO545gigwIbDAkF+2fdLB
AgMBAAGjUDBOMB0GA1UdDgQWBBR87cyPwGS6qtvw6DwQkt4WX+9PmDAfBgNVHSME
GDAWgBR87cyPwGS6qtvw6DwQkt4WX+9PmDAMBgNVHRMEBTADAQH/MA0GCSqGSIb3
DQEBBQUAA4GBAAmmo50E53Kf109XlXGlYYU8EUIgnpefG7/bR1z0XzbwNtxjeCYu
laiXnqf++nn+gwJ9IQk1Kqy3ZqvByBQ0s4jMlY59B6rOTyds/a8hhXG8/wzPK85D
6nHjFwZMEPT5aUGtCKkTnBzf+cKN3CKJtAQGB0cl7y1fCpuXZdUWMsSB
-----END CERTIFICATE-----"""
CERT_DEV = "0xCD1F95097E3247A4E0892F41F0A8CBC989E60C55F1620F60F2" \
           "9E6D4E5EC9F4983B58E73EA022E47465DFBE3B67F1E87B2D5AF6" \
           "852316261ABF42F28E869D9C9B500338F731AECB50B0E610C26D" \
           "90FBE83096575C42DF5188DA6F0A44A8EDBFB70CCB06FD87A365" \
           "03E5DA2C175FA1207A1F3B9E3982283021B0C0905FB67DD2C1"

URL_API_REL = 'https://osapi.dmm.com/social_pc/rest'
CERTIFICATE_REL = """-----BEGIN CERTIFICATE-----
MIIB/jCCAWegAwIBAgIJAOeNkqefvPO0MA0GCSqGSIb3DQEBBQUAMBgxFjAUBgNV
BAMMDW9zYXBpLmRtbS5jb20wHhcNMTYwNTEwMDAyOTA4WhcNMTgwNzEwMDAyOTA4
WjAYMRYwFAYDVQQDDA1vc2FwaS5kbW0uY29tMIGfMA0GCSqGSIb3DQEBAQUAA4GN
ADCBiQKBgQC39WdRdT7C4t3Ry6+Z6W8lqq4gUbn8m7cwgkcgCHAsSNuuyuphm1pA
9wQN8br0VXsDE5JR+q9cVmAlVyyAb6X3kKSrV2A7xzWHe6xRe8ZbN1BchELh8qQc
H6RDlHeapz272srdB+vWFC+sqXuVi1/S4lK02y6RvfOafpMUo9MXTwIDAQABo1Aw
TjAdBgNVHQ4EFgQUkegUumceQict2UugU/KzmH+jB1QwHwYDVR0jBBgwFoAUkegU
umceQict2UugU/KzmH+jB1QwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQUFAAOB
gQAv2VqZ4xGcG1gHH30HeSlA712ldTPKSGG7hmYJzh0jDH6dRcrXP22S+mGCox3a
pa5Wl62H5O3Lk49JhTeFHihbNlgif4n0jAg4ZkdNYWwlOYkcTv2MfG4gOB3FcySE
zSq4mpk+lGyJbdu0aboydSG9AtvtR61at/P0N2xm5N4OSw==
-----END CERTIFICATE-----"""
CERT_REL = "0xB7F56751753EC2E2DDD1CBAF99E96F25AAAE2051B9FC9BB730" \
           "82472008702C48DBAECAEA619B5A40F7040DF1BAF4557B031392" \
           "51FAAF5C566025572C806FA5F790A4AB57603BC735877BAC517B" \
           "C65B37505C8442E1F2A41C1FA44394779AA73DBBDACADD07EBD6" \
           "142FACA97B958B5FD2E252B4DB2E91BDF39A7E9314A3D3174F"

#ApiRequestMaker = ApiRequestMakerBase

def _makeRequestUrl(osa_util, path):
    if osa_util.appparam.sandbox:
        return URL_API_DEV + path
    else:
        return URL_API_REL + path


#=========================
# People.
class PeopleApiRequest(ApiRequest):
    """Peopleリクエスト.
    """
    def prework(self):
        self._method = 'GET'
        guid = self.requestdata.guid
        selector = self.requestdata.selector
        pid = self.requestdata.pid
        fields = self.requestdata.fields
        is_list = False
        
        if selector in ('@friends', '@all'):
            if pid:
                self._url = _makeRequestUrl(self.osa_util, '/people/%s/%s/%s' % (guid, selector, pid))
            else:
                self._url = _makeRequestUrl(self.osa_util, '/people/%s/%s' % (guid, selector))
                is_list = True
        else:
            self.requestdata.selector = '@self'
            self._url = _makeRequestUrl(self.osa_util, '/people/%s/@self' % guid)
        
        self._queryparams = {}
        if fields:
            self._queryparams['fields'] = ','.join(fields)
        if is_list:
            count = self.requestdata.count
            startIndex = self.requestdata.startIndex
            filterBy = self.requestdata.filterBy
            filterOp = self.requestdata.filterOp
            filterValue = self.requestdata.filterValue
            if 0 < count:
                self._queryparams['count'] = count
            if -1 < startIndex:
                self._queryparams['startIndex'] = startIndex
            if filterBy and filterOp and filterValue:
                self._queryparams['filterBy'] = filterBy
                self._queryparams['filterOp'] = filterOp
                self._queryparams['filterValue'] = filterValue
        
        self._oauthparams = {}
    
    def responseToData(self, response):
        json_obj = Json.decode(response)
        entry = json_obj['entry']
        if type(entry) is list:
            return [self.dictdataToPeople(data) for data in entry]
        else:
            return self.dictdataToPeople(entry)
    
    def dictdataToPeople(self, dictdata):
        people = People()
        
        people._id = dictdata.get('id')
        people._nickname = dictdata.get('nickname')
        people._displayName = dictdata.get('displayName')
        people._aboutMe = dictdata.get('aboutMe')
        people._profileUrl = dictdata.get('profileUrl')
        people._thumbnailUrl = dictdata.get('thumbnailUrl')
        people._thumbnailUrlSmall = dictdata.get('thumbnailUrlSmall')
        people._thumbnailUrlLarge = dictdata.get('thumbnailUrlLarge')
        people._thumbnailUrlHuge = dictdata.get('thumbnailUrlHuge')
        people._hasApp = dictdata.get('hasApp')
        people._userType = dictdata.get('userType')
        
        people.lock()
        
        return people

#=========================
# Activity.
class ActivityApiRequest(ApiRequest):
    def prework(self):
        self._method = 'POST'
        self._url = _makeRequestUrl(self.osa_util, '/activities/@me/@self/@app')
        self._postdata = {
            'title' : self.requestdata.title,
        }
        for k in ('url','mobileUrl','touchUrl'):
            v = getattr(self.requestdata, k)
            if v:
                self._postdata[k] = v

#=========================
# Message.
class MessageApiRequest(ApiRequest):
    def prework(self):
        self._method = 'POST'
        self._url = _makeRequestUrl(self.osa_util, '/messages/@me/@outbox')
        self._postdata = {
            'title' : self.requestdata.title,
            'recipients' : self.requestdata.recipients,
        }
        urls = []
        for urltype, url in self.requestdata.urls.items():
            if url:
                urls.append({
                    'value' : url,
                    'type' : urltype,
                })
        self._postdata['urls'] = urls

#=========================
# Payment.
class PaymentGetApiRequest(ApiRequest):
    
    BATCH_ONLY = True
    
    def prework(self):
        self._method = 'GET'
        guid = self.requestdata.guid
        paymentId = self.requestdata.paymentId
        self._url = _makeRequestUrl(self.osa_util, '/payment/%s/@self/@app/%s' % (guid, paymentId))
    
    def getLocalResponse(self):
        response = self.getResponseApi()
        if self._response_is_pure:
            return response
        return self.responseToData(response)
    
    def responseToData(self, response):
        json_obj = Json.decode(response)
        entry = json_obj['entry']
        
        payment = PaymentData()
        
        payment._paymentId = entry.get('paymentId')
        payment._appId = entry.get('appId')
        payment._userId = self.requestdata.guid
        payment._status = entry.get('status')
        payment._callbackUrl = entry.get('callbackUrl')
        payment._finishPageUrl = entry.get('finishPageUrl')
        payment._transactionUrl = entry.get('transactionUrl')
        payment._message = entry.get('message')
        payment._orderedTime = entry.get('orderedTime')
        payment._executeTime = entry.get('executedTime')
        payment._paymentItems = tuple([self.dictdataToPaymentItem(dictdata) for dictdata in entry.get('paymentItems', [])])
        
        payment.lock()
        return payment
    
    def dictdataToPaymentItem(self, dictdata):
        item = PaymentItem()
        str_item_id = dictdata.get('itemId')
        if str_item_id.isdigit():
            item.itemId = int(dictdata.get('itemId'))
        else:
            item.itemId = str_item_id
        item.itemName = dictdata.get('itemName')
        item.unitPrice = int(dictdata.get('unitPrice'))
        item.quantity = int(dictdata.get('quantity'))
        item.imageUrl = dictdata.get('imageUrl')
        item.description = dictdata.get('description')
        return item

class PaymentPostApiRequest(ApiRequest):
    def prework(self):
        self._method = 'POST'
        self._url = _makeRequestUrl(self.osa_util, '/payment/@me/@self/@app')
        
        paymentItems = []
        for item in self.requestdata.paymentItems:
            paymentItems.append({
                'itemId' : item.itemId,
                'itemName' : item.itemName,
                'unitPrice' : item.unitPrice,
                'quantity' : item.quantity,
                'imageUrl' : item.imageUrl,
                'description' : item.description,
            })
        
        self._postdata = {
            'callbackUrl' : self.requestdata.callbackUrl,
            'finishPageUrl' : self.requestdata.finishPageUrl,
            'message' : self.requestdata.message,
            'paymentItems' : paymentItems,
        }
    
    def getLocalResponse(self):
        response = self.getResponseApi()
        if self._response_is_pure:
            return response
        return self.responseToData(response)
    
    def responseToData(self, response):
        json_obj = Json.decode(response)
        entry = json_obj['entry']
        
        payment = PaymentPostResultData()
        
        payment._paymentId = entry.get('paymentId')
        payment._status = entry.get('status')
        payment._transactionUrl = entry.get('transactionUrl')
        payment._orderedTime = entry.get('orderedTime')
        
        payment.lock()
        return payment

#=========================
# Inspection.

def _dictdataToInspectionData(dictdata):
    status = int(dictdata.get('status', -1))
    if not status in (0, 1):
        return None
    inspection = InspectionData()
    inspection._textId = dictdata.get('textId')
    inspection._appId = dictdata.get('appId')
    inspection._authorId = dictdata.get('authorId')
    inspection._ownerId = dictdata.get('ownerId')
    inspection._data = dictdata.get('data')
    inspection._status = status
    inspection._ctime = dictdata.get('ctime')
    inspection._mtime = dictdata.get('mtime')
    inspection.lock()
    return inspection

class InspectionGetApiRequest(ApiRequest):
    def prework(self):
        self._method = 'GET'
        textId = self.requestdata.textId
        if type(textId) is list:
            textId = ','.join(textId)
        self._url = _makeRequestUrl(self.osa_util, '/inspection/@app/%s' % textId)
    
    def responseToData(self, response):
        json_obj = Json.decode(response)
        entry = json_obj['entry']
        if type(entry) is not list:
            entry = [entry]
        
        datalist = []
        for dictdata in entry:
            inspection = _dictdataToInspectionData(dictdata)
            if inspection:
                datalist.append(inspection)
        return datalist
    
    def processHttpError(self, err):
        if err.code == 404:
            return Json.encode({'entry':[]})
        raise err

class InspectionPostApiRequest(ApiRequest):
    def prework(self):
        self._method = 'POST'
        self._url = _makeRequestUrl(self.osa_util, '/inspection/@app')
        self._postdata = {
            'data' : self.requestdata.data,
        }
    
    def responseToData(self, response):
        json_obj = Json.decode(response)
        entry = json_obj['entry'][0]
        return _dictdataToInspectionData(entry)

class InspectionPutApiRequest(ApiRequest):
    def prework(self):
        self._method = 'PUT'
        textId = self.requestdata.textId
        self._url = _makeRequestUrl(self.osa_util, '/inspection/@app/%s' % textId)
        self._postdata = {
            'data' : self.requestdata.data,
        }
    
    def responseToData(self, response):
        if response:
            return True
        else:
            return False
    
    def processHttpError(self, err):
        if err.code == 404:
            return None
        raise err

class InspectionDeleteApiRequest(ApiRequest):
    def prework(self):
        self._method = 'DELETE'
        textId = self.requestdata.textId
        if type(textId) is list:
            textId = ','.join(textId)
        self._url = _makeRequestUrl(self.osa_util, '/inspection/@app/%s' % textId)
    
    def responseToData(self, response):
        if response:
            return True
        else:
            return False
    
    def processHttpError(self, err):
        if err.code == 404:
            return None
        raise err

#=========================
# Ignorelist.
class IgnorelistApiRequest(ApiRequest):
    def prework(self):
        self._method = 'GET'
        guid = self.requestdata.guid
        pid = self.requestdata.pid
        if pid:
            self._url = _makeRequestUrl(self.osa_util, '/ignorelist/%s/@all/%s' % (guid, pid))
        else:
            self._url = _makeRequestUrl(self.osa_util, '/ignorelist/%s/@all' % guid)
            self._queryparams = {}
            count = self.requestdata.count
            startIndex = self.requestdata.startIndex
            if 0 < count:
                self._queryparams['count'] = count
            if -1 < startIndex:
                self._queryparams['startIndex'] = startIndex
    
    def responseToData(self, response):
        json_obj = Json.decode(response)
        entry = json_obj.get('entry')
        
        self.osa_util.logger.info('ignorelist entry:%s' % entry)
        
        if entry is None:
            self.osa_util.logger.info('ignorelist is None')
            return None
        elif not isinstance(entry, list):
            entry = [entry]
        
        datalist = []
        for dictdata in entry:
            ignorelist = IgnorelistData()
            
            ignorelist._id = dictdata.get('id')
            ignorelist._ignorelistId = dictdata.get('ignorelistId')
            
            ignorelist.lock()
            datalist.append(ignorelist)
        
        return datalist

class ApiRequestMaker(ApiRequestMakerBase):
    
    #=========================
    # People.
    @classmethod
    def makePeopleApiRequest(cls, osa_util, requestdata):
        return PeopleApiRequest(osa_util, requestdata)
    
    #=========================
    # Activity.
    @classmethod
    def makeActivityApiRequest(cls, osa_util, requestdata):
        return ActivityApiRequest(osa_util, requestdata)
    
    #=========================
    # Message.
    @classmethod
    def makeMessageApiRequest(cls, osa_util, requestdata):
        return MessageApiRequest(osa_util, requestdata)
    
    #=========================
    # Payment.
    @classmethod
    def makePaymentGetApiRequest(cls, osa_util, requestdata):
        return PaymentGetApiRequest(osa_util, requestdata)
    @classmethod
    def makePaymentPostApiRequest(cls, osa_util, requestdata):
        return PaymentPostApiRequest(osa_util, requestdata)
    
    #=========================
    # Inspection.
    @classmethod
    def makeInspectionGetApiRequest(cls, osa_util, requestdata):
        return InspectionGetApiRequest(osa_util, requestdata)
    @classmethod
    def makeInspectionPostApiRequest(cls, osa_util, requestdata):
        return InspectionPostApiRequest(osa_util, requestdata)
    @classmethod
    def makeInspectionPutApiRequest(cls, osa_util, requestdata):
        return InspectionPutApiRequest(osa_util, requestdata)
    @classmethod
    def makeInspectionDeleteApiRequest(cls, osa_util, requestdata):
        return InspectionDeleteApiRequest(osa_util, requestdata)
    
    #=========================
    # Ignorelist.
    @classmethod
    def makeIgnorelistApiRequest(cls, osa_util, requestdata):
        return IgnorelistApiRequest(osa_util, requestdata)
