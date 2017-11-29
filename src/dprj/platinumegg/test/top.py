# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType

class ApiTest(ApiTestBase):
    """Topページ.
    """
    (
        TEST_INSTALL,       # 初回アクセス.
        TEST_NOT_REGIST,    # 未登録.
        TEST_TUTORIAL,      # チュートリアル中.
        TEST_ALLEND,        # 全て完了済み.
    ) = range(4)
    TEST_MODE = TEST_INSTALL
    
    def setUp(self):
        # DMMID.
        dmmid = None
        if ApiTest.TEST_MODE == ApiTest.TEST_INSTALL:
            player = self.create_dummy(DummyType.PLAYER)
            dmmid = u'%s' % (player.id + 1)
        elif ApiTest.TEST_MODE == ApiTest.TEST_NOT_REGIST:
            player = self.create_dummy(DummyType.PLAYER, regist=False)
            dmmid = player.dmmid
        elif ApiTest.TEST_MODE == ApiTest.TEST_TUTORIAL:
            player = self.create_dummy(DummyType.PLAYER, tutoend=False)
            dmmid = player.dmmid
        elif ApiTest.TEST_MODE == ApiTest.TEST_ALLEND:
            player = self.create_dummy(DummyType.PLAYER)
            dmmid = player.dmmid
        else:
            raise AppTestError(u'Unknown TestMode. %s' % ApiTest.TEST_MODE)
        
        # お知らせ.
        for _ in range(5):
            self.create_dummy(DummyType.INFOMATION_MASTER)
            self.create_dummy(DummyType.EVENT_BANNER_MASTER)
            self.create_dummy(DummyType.TOP_BANNER_MASTER)
        
        self.__dmmid = dmmid
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__dmmid,
        }
    
    def check(self):
        if not self.response.get('url_topimage'):
            raise AppTestError(u'Top画像が設定されていない')
        
        if ApiTest.TEST_MODE == ApiTest.TEST_ALLEND:
            if not self.response.get('slidebanners'):
                raise AppTestError(u'トップページバナーが設定されてない')
            if not self.response.get('eventbanners'):
                raise AppTestError(u'イベントバナーが設定されてない')
            if not (self.response.get('infomations') or self.response.get('infomation')):
                raise AppTestError(u'お知らせが設定されてない')
        else:
            if not self.response.get('url_enter'):
                raise AppTestError(u'遷移先のURLが設定されてない')
