# -*- coding: utf-8 -*-
from platinumegg.lib.thread import ThreadBase
from oauth import oauth
from platinumegg.lib.strutil import StrUtil
import urllib
import urllib2
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.lib.apperror import ErrorUtil, AppError
from platinumegg.lib.pljson import Json
from platinumegg.lib import timezone
import settings_sub

class ApiNames:
    People = 'People'
    Activity = 'Activity'
    Message = 'Message'
    PaymentGet = 'PaymentGet'
    PaymentPost = 'PaymentPost'
    InspectionGet = 'InspectionGet'
    InspectionPost = 'InspectionPost'
    InspectionPut = 'InspectionPut'
    InspectionDelete = 'InspectionDelete'
    Ignorelist = 'Ignorelist'
    
    PaymentLog = 'PaymentLog'


class ApiRequest(ThreadBase):
    
    BATCH_ONLY = False
    
    def __init__(self, osa_util, requestdata):
        ThreadBase.__init__(self)
        self.requestdata = requestdata
        self.osa_util = osa_util
        self._url = ''
        self._method = 'GET'
        self._postdata = {}
        self._queryparams = {}
        self._oauthparams = {}
        
        # バッチモード時はヘッダの内容が変わることがある.
        self._is_batch_mode = self.BATCH_ONLY or self.osa_util.is_admin_access
        self._response_is_pure = False
        
    
    def prework(self):
        pass
    def responseToData(self, response):
        return response
    def processHttpError(self, err):
        raise err
    def getLocalResponse(self):
        return []
    
    def get_url(self):
        return self._url
    
    def get_queryparams(self):
        return self._queryparams
    
    def get_body(self):
        postdata = self.get_postdata()
        if postdata:
            return Json.encode(self.get_postdata())
        else:
            return ''
    
    def get_postdata(self):
        return self._postdata
    
    def get_http_method(self):
        return self._method
    
    def get_content_type(self):
        return 'application/json; charset=utf-8'
    
    def get_oauthparams(self):
        return self._oauthparams
    
    def get_requestor_id(self):
        return self.osa_util.viewer_id
    
    def get_certificate(self):
        return None
    
    def work(self):
        self.prework()
        if settings_sub.IS_LOCAL or settings_sub.IS_BENCH:
            return self.getLocalResponse()
        else:
            response = self.getResponseApi()
            if self._response_is_pure:
                return response
            return self.responseToData(response)
    
    def __makeOAuthRequest(self, params, *args):
        if self._is_batch_mode:
            oauth_token = None
        else:
            oauth_token = self.osa_util.oauth_token
        outhparams = self.get_oauthparams()
        
        if self._is_batch_mode:
            pass
        else:
            params['xoauth_requestor_id'] = self.get_requestor_id()
        outhparams.update(params)
        
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.osa_util.consumer,
            http_method=self.get_http_method(),
            http_url=self.get_url(),
            token=oauth_token,
            parameters=outhparams,
        )
        request.sign_request(
            oauth.OAuthSignatureMethod_HMAC_SHA1(),
            self.osa_util.consumer,
            oauth_token
        )
        return request
    
    def __getResponseApi(self, funcMakeRequest):
        ope_url = self.get_url()
        post_data = self.get_postdata()
        queryparams = self.get_queryparams()
        http_method = self.get_http_method()
        
        if type(post_data) == unicode:
            post_data = StrUtil.to_s(post_data, 'utf-8')
        
        self.osa_util.logger.trace('ope_url:' + ope_url)
        
        request = funcMakeRequest(queryparams)
        
        headers = request.to_header()
        xoauth_requestor_id = queryparams.get('xoauth_requestor_id')
        if xoauth_requestor_id:
            headers['Authorization'] = '%s, xoauth_requestor_id="%s"' % (headers['Authorization'], xoauth_requestor_id)
#            del queryparams['xoauth_requestor_id']
        headers['Content-Type'] = self.get_content_type()
        
        # Query the user's personal info and print them
        if queryparams:
            uri = '%s?%s' % (request.get_normalized_http_url(), urllib.urlencode(queryparams))
        else:
            uri = request.get_normalized_http_url()
        body = self.get_body()
        
        logs = [
            "HTTP Method:%s" % http_method,
            "API_URI:%s" % uri,
        ]
        logs.append('request headers:')
        logs.extend(['\t%s: %s' % (k,v) for k,v in headers.items()])
        logs.append('request body:')
        logs.append(body)
        log = '\n'.join(logs)
        self.osa_util.logger.trace(log)
        
        if self._is_batch_mode:
            timeout = None
        else:
            timeout = 3
        
        tmp = None
        try:
            tmp = self.osa_util.httpopen(uri, body, http_method, headers, self.get_certificate(), timeout=timeout)
            response = tmp.read()
            self.osa_util.logger.info('getResponseApi response:%s' % response)
            return response
        except urllib2.HTTPError, er:
            if tmp is not None and tmp.fp:
                tmp.fp._sock.recv = None
            
            if self.osa_util.is_dbg:
                if er.fp is None:
                    error_message = str(er)
                else:
                    error_message = er.read()
                self.osa_util.logger.error(self.osa_util.logger.to_string())
                self.osa_util.logger.error('getResponseApi er_code:%s %s' % (er.code, error_message))
            
            if er.code == 401:
                info = str(er)
                now = OSAUtil.get_now(timezone.TZ_DEFAULT)
                delta = self.osa_util.getElpsedTime()
                str_body = None
                try:
                    str_body = '%s' % post_data
                except:
                    self.osa_util.logger.error('str_body can not translate... %s' % ErrorUtil.getLastErrorMessage())
                    pass
                er_response = ''
                if er.fp is not None:
                    er_response = er.read()
                temp_log = ('getResponseApi log:%s' % log
                    + 'now:%s\n' % now
                    + 'elapsed time: %d.%06d sec.\n' % (delta.seconds, delta.microseconds)
                    + 'body:%s' % str_body
                    + 'er info:%s\n' % info
                    + 'er read:%s\n' % er_response
                    + 'error:%s\n' % er
                )
                self.osa_util.logger.warning(temp_log)
            return self.processHttpError(er)
        except urllib2.URLError, urlerr:
            raise AppError('UrlError:reason:%s' % urlerr.reason)
    
    def getResponseApi(self):
        """ OAuth ヘッダを付加したリクエストで オープンソーシャルAPIからレスポンスを取得.
        """
        return self.__getResponseApi(self.__makeOAuthRequest)

class ApiRequestMakerBase:
    @classmethod
    def makeApiRequest(cls, apiname, osa_util, requestdata):
        funcname = 'make%sApiRequest' % apiname
        func = getattr(cls, funcname)
        return func(osa_util, requestdata)
    
    #=========================
    # People.
    @classmethod
    def makePeopleApiRequest(cls, osa_util, requestdata):
        return None
    
    #=========================
    # Activity.
    @classmethod
    def makeActivityApiRequest(cls, osa_util, requestdata):
        return None
    
    #=========================
    # Message.
    @classmethod
    def makeMessageApiRequest(cls, osa_util, requestdata):
        return None
    
    #=========================
    # Payment.
    @classmethod
    def makePaymentGetApiRequest(cls, osa_util, requestdata):
        return None
    @classmethod
    def makePaymentPostApiRequest(cls, osa_util, requestdata):
        return None
    
    #=========================
    # Inspection.
    @classmethod
    def makeInspectionGetApiRequest(cls, osa_util, requestdata):
        return None
    @classmethod
    def makeInspectionPostApiRequest(cls, osa_util, requestdata):
        return None
    @classmethod
    def makeInspectionPutApiRequest(cls, osa_util, requestdata):
        return None
    @classmethod
    def makeInspectionDeleteApiRequest(cls, osa_util, requestdata):
        return None
    
    #=========================
    # Ignorelist.
    @classmethod
    def makeIgnorelistApiRequest(cls, osa_util, requestdata):
        return None
    
    #=========================
    # PaymentLog.
    @classmethod
    def makePaymentLogApiRequest(cls, osa_util, requestdata):
        return None


