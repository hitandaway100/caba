# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class PcTestBase(ApiTestBase):
    
    @classmethod
    def makeRequestUrl(cls, api):
        return "/pc/%s/" % api
    
    def checkResponseStatus(self):
        status = self.response.get(Defines.STATUS_KEY_NAME)
        if status != CabaretError.Code.OK:
            raise AppTestError(u'ステータスが正しくない. %s(%s)' % (CabaretError.getCodeString(status), status))
    
    @property
    def resultbody(self):
        return self.response.get('result')
