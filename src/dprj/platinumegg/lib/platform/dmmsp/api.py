# -*- coding: utf-8 -*-

from platinumegg.lib.platform.api.request import ApiRequestMakerBase, ApiRequest
from platinumegg.lib.platform.api.objects import People, PaymentData,\
    PaymentItem, PaymentPostResultData, InspectionData, IgnorelistData
from platinumegg.lib.pljson import Json
import urllib


URL_API_DEV = 'http://sbx-osapi.dmm.com/social_sp/rest'
URL_API_REL = 'https://osapi.dmm.com/social_sp/rest'

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
        item.itemId = int(dictdata.get('itemId'))
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

class PaymentLogApiRequest(ApiRequest):
    """PaymentLogApi.
    """
    
    BATCH_ONLY = True
    
    def prework(self):
        self._method = 'POST'
        if self.osa_util.appparam.sandbox:
            self._url = u'http://api.developer-freegames.dmm.com/sbx-payment/'
        else:
            self._url = u'http://api.developer-freegames.dmm.com/payment/'
        
        self._postdata = {
            'app_id' : self.osa_util.appparam.app_id,
            'date' : self.requestdata.date.strftime('%Y-%m-%d'),
            'device' : self.requestdata.device or 'sp',
            'overwrite' : 'true' if self.requestdata.overwrite else 'false',
            'data' : self.requestdata.get_xmldata(),
#            'data' : '',
        }
    
    def get_content_type(self):
        return 'application/x-www-form-urlencoded'
    
    def get_body(self):
        return urllib.urlencode(self._postdata)
    
    def get_oauthparams(self):
        return self._postdata
    
    def getLocalResponse(self):
        return self.responseToData('{"status":"OK","message":""}')
    
    def responseToData(self, response):
        json_obj = Json.decode(response)
        status = json_obj.get('status', 'NG')
        message = json_obj.get('message', 'Message Empty')
        return {
            'status' : status,
            'message' : message,
            'is_success' : status == 'OK',
            'data' : response,
        }

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
    
    #=========================
    # PaymentLog.
    @classmethod
    def makePaymentLogApiRequest(cls, osa_util, requestdata):
        return PaymentLogApiRequest(osa_util, requestdata)
