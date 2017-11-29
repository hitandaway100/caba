# -*- coding: utf-8 -*-
from platinumegg.lib.apperror import AppError


class APIObjectMeta(type):
    
    def __init__(cls, clsname, bases, attrs):
        super(APIObjectMeta, cls).__init__(clsname, bases, attrs)
        
        attr_meta = attrs.pop('Meta', None)
        if attr_meta:
            attrbutes = attr_meta.ATTRIBUTES or {}
            cls._fields = {}
            for name,default_v in attrbutes.items():
                cls._fields['_' + name] = default_v

class APIObject:
    __metaclass__ = APIObjectMeta
    
    def __init__(self):
        self.__dict__['_APIObject__locked'] = False
        self.__dict__['_fields'] = {}
    
    def lock(self):
        self.__dict__['_APIObject__locked'] = True
    
    def __getattr__(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            cls = self.__class__
            att = name
            if name[0] == '_':
                att = name[1:]
            if self._fields.has_key(att):
                return self._fields[att]
            elif cls._fields.has_key('_' + att):
                return cls._fields['_' + att]
            else:
                raise AttributeError('%s instance do not have %s' % (self.__class__, name))
    
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            self.__dict__[name] = value
        else:
            cls = self.__class__
            att = name
            if name[0] == '_':
                att = name[1:]
            if cls._fields.has_key(att) or (not self.__locked and cls._fields.has_key('_'+att)):
                self._fields[att] = value
            else:
                raise AttributeError('%s instance do not have %s' % (self.__class__, name))
        return value

#====================================================
# People.
class PeopleRequestData:
    """Peopleのリクエストデータ.
    """
    guid = '@me'
    selector = '@self'
    pid = None
    fields = None
    count = -1
    startIndex = -1
    filterBy = None
    filterOp = None
    filterValue = None
    
    @staticmethod
    def createForPeople(uid):
        ins = PeopleRequestData()
        ins.guid = uid
        ins.selector = '@self'
        return ins
    @staticmethod
    def createForFriend(uid):
        ins = PeopleRequestData()
        ins.guid = uid
        ins.selector = '@friends'
        return ins
    @staticmethod
    def createForAll(uid):
        ins = PeopleRequestData()
        ins.guid = uid
        ins.selector = '@all'
        return ins
    
class People(APIObject):
    """ユーザープロフィール情報.
    """
    class Meta:
        ATTRIBUTES = {
            'id' : '',
            'nickname' : '',
            'displayName' : '',
            'aboutMe' : '',
            'profileUrl' : '',
            'thumbnailUrl' : '',
            'thumbnailUrlSmall' : '',
            'thumbnailUrlLarge' : '',
            'thumbnailUrlHuge' : '',
            'hasApp' : False,
            'userType' : '',
        }
    @staticmethod
    def makeNotFound(dmmid=''):
        ins = People()
        ins.id = dmmid
        ins.nickname = u'名無し%s' % dmmid
        ins.displayName = u'名無し%s' % dmmid
        ins.lock()
        return ins

#====================================================
# Activity.
class ActivityRequestData:
    """Activityのリクエストデータ.
    """
    title = None
    url = None
    mobileUrl = None
    touchUrl = None

#====================================================
# Message.
class MessageRequestData:
    """Messageのリクエストデータ.
    """
    title = ''
    body = ''
    recipients = None
    _urls = None
    
    @property
    def urls(self):
        if self._urls is None:
            self._urls = {
                'mobile' : None,
                'touch' : None,
                'canvas' : None,
            }
        return self._urls

#====================================================
# Payment.

class PaymentItem:
    """Paymentの商品データ.
    """
    itemId = ""
    itemName = ""
    unitPrice = 0
    quantity = 0
    imageUrl = ""
    description = ""

class PaymentData(APIObject):
    """Paymentのデータ.
    """
    class Status:
        CREATE = 0
        START = 1
        COMPLETED = 2
        CANCEL = 3
        TIMEOUT = 4
    
    class Meta:
        ATTRIBUTES = {
            'paymentId' : '',
            'appId' : 0,
            'userId' : '',
            'status' : 0,
            'callbackUrl' : '',
            'finishPageUrl' : '',
            'transactionUrl' : '',
            'message' : '',
            'paymentItems' : (),
            'orderedTime' : None,
            'executeTime' : None,
        }

class PaymentPostResultData(APIObject):
    """Payment作成完了データ.
    """
    class Meta:
        ATTRIBUTES = {
            'paymentId' : '',
            'status' : 0,
            'transactionUrl' : '',
            'orderedTime' : None,
        }

class PaymentGetRequestData:
    """Payment取得リクエストデータ.
    """
    guid = ''
    paymentId = ''

class PaymentPostRequestData:
    """Payment作成リクエストデータ.
    """
    callbackUrl = ''
    finishPageUrl = ''
    message = ''
    _paymentItems = None
    
    @property
    def paymentItems(self):
        if self._paymentItems is None:
            self._paymentItems = []
        return self._paymentItems
    
    def addItem(self, itemId, itemName, unitPrice, quantity, imageUrl, description):
        ins = PaymentItem()
        ins.itemId = itemId
        ins.itemName = itemName
        ins.unitPrice = unitPrice
        ins.quantity = quantity
        ins.imageUrl = imageUrl
        ins.description = description
        self.paymentItems.append(ins)

class PaymentLogRequestData:
    """PaymentLogAPIリクエストデータ.
    """
    ENTRY_NUM_MAX = 500
    
    def __init__(self, date, device, overwrite):
        self.date = date
        self.device = device
        self.overwrite = overwrite
        self.paymentList = []
    
    def addPaymentEntry(self, paymentId, unitPrice, quantity):
        if PaymentLogRequestData.ENTRY_NUM_MAX <= len(self.paymentList):
            raise AppError("PaymentLogRequestData.addPaymentEntry:over limit.")
        self.paymentList.append((paymentId, unitPrice, quantity))
    
    def get_xmldata(self):
        XML_FORMAT = '<item><payment_id>{paymentId}</payment_id><unitPrice>{unitPrice}</unitPrice><quantity>{quantity}</quantity><totalPoint>{totalPoint}</totalPoint></item>'
        arr = [XML_FORMAT.format(paymentId=paymentId, unitPrice=unitPrice, quantity=quantity, totalPoint=unitPrice*quantity) for paymentId, unitPrice, quantity in self.paymentList]
        return '<game>%s</game>' % (''.join(arr))

#====================================================
# Inspection.
class InspectionData(APIObject):
    """Inspectionのデータ.
    """
    class Meta:
        ATTRIBUTES = {
            'textId' : '',
            'appId' : '',
            'authorId' : '',
            'ownerId' : '',
            'data' : '',
            'status' : 0,
            'ctime' : None,
            'mtime' : None,
        }

class InspectionGetRequestData:
    """Inspection取得リクエストデータ.
    """
    textId = None
    
class InspectionPostRequestData:
    """Inspection投稿リクエストデータ.
    """
    data = ""
    
class InspectionPutRequestData:
    """Inspection更新リクエストデータ.
    """
    textId = ""
    data = ""
    
class InspectionDeleteRequestData:
    """Inspection削除リクエストデータ.
    """
    textId = []
    

#====================================================
# Ignorelist.
class IgnorelistData(APIObject):
    """Ignorelistデータ.
    """
    class Meta:
        ATTRIBUTES = {
            'id' : '',
            'ignorelistId' : '',
        }

class IgnorelistRequestData:
    """Ignorelist取得リクエストデータ.
    """
    guid = '@me'
    pid = ''
    count = -1
    startIndex = 0

