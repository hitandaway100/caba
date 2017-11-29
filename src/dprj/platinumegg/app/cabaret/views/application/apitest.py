# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.lib.platform.api.objects import PeopleRequestData,\
    ActivityRequestData, MessageRequestData, PaymentGetRequestData,\
    PaymentPostRequestData, InspectionGetRequestData, InspectionPostRequestData,\
    InspectionPutRequestData, InspectionDeleteRequestData, IgnorelistRequestData
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AppHandler):
    """スマホ版のAPIのテスト.
    """
    def checkUser(self):
        if not self.osa_util.is_dbg_user:
            raise CabaretError(u'認証エラー', CabaretError.Code.NOT_AUTH)
    
    def process(self):
        if self.request.method == 'POST':
            self.processApiTest()
        
        self.html_param.update({
            'url_movie_test' : self.makeAppLinkUrl('/template_test/test/movie_test.html'),
        })
        self.osa_util.write_html('test/api_test.html', self.html_param)
    
    def processApiTest(self):
        apiname = self.request.get('_api')
        makeFunc = getattr(self, 'makeRequest%s' % apiname)
        requestdata = makeFunc()
        request = self.osa_util.makeApiRequest(apiname, requestdata)
        request._response_is_pure = True    # レスポンスをそのままの形で受け取りたい.
        self.addAppApiRequest('test', request)
        ret_data = self.execute_api()
        data = ret_data['test'].get()
        self.html_param['result'] = {
             'apiname' : apiname,
             'data' : data,
        }
    
    def makeRequestPeople(self):
        requestdata = PeopleRequestData()
        requestdata.guid = self.request.get('_guid')
        requestdata.selector = self.request.get('_selector')
        requestdata.pid = self.request.get('_pid')
        return requestdata
    
    def makeRequestActivity(self):
        requestdata = ActivityRequestData()
        requestdata.title = self.request.get('_title')
        return requestdata
    
    def makeRequestMessage(self):
        requestdata = MessageRequestData()
        requestdata.title = self.request.get('_title')
        requestdata.body = self.request.get('_body')
        requestdata.recipients = self.request.get('_recipients', '').split(',')
        return requestdata
    
    def makeRequestPaymentGet(self):
        requestdata = PaymentGetRequestData()
        requestdata.guid = self.request.get('_guid')
        requestdata.paymentId = self.request.get('_paymentId')
        return requestdata
    
    def makeRequestPaymentPost(self):
        requestdata = PaymentPostRequestData()
        requestdata.callbackUrl = self.url_cgi + UrlMaker.top()
        requestdata.finishPageUrl = self.url_cgi + UrlMaker.top()
        requestdata.message = u'課金テストです'
        requestdata.addItem(u'01234', u'テストアイテム', 100, 2, 'http://ideawalk.net/twitter/image/purazuma', u'課金テストです')
        return requestdata
    
    def makeRequestInspectionGet(self):
        requestdata = InspectionGetRequestData()
        requestdata.textId = self.request.get('_textId')
        return requestdata
    
    def makeRequestInspectionPost(self):
        requestdata = InspectionPostRequestData()
        requestdata.data = self.request.get('_data')
        return requestdata
    
    def makeRequestInspectionPut(self):
        requestdata = InspectionPutRequestData()
        requestdata.textId = self.request.get('_textId')
        requestdata.data = self.request.get('_data')
        return requestdata
    
    def makeRequestInspectionDelete(self):
        requestdata = InspectionDeleteRequestData()
        requestdata.textId = self.request.get('_textId')
        return requestdata
    
    def makeRequestIgnorelist(self):
        requestdata = IgnorelistRequestData()
        requestdata.guid = self.request.get('_guid')
        requestdata.pid = self.request.get('_pid')
        return requestdata

def main(request):
    return Handler.run(request)
