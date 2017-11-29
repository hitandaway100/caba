# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Title import TitlePlayerData
import datetime

class ApiTest(ApiTestBase):
    """称号獲得 設定.
    """
    
    def setUp(self):
        self.__now = OSAUtil.get_now()
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 名誉ポイント.
        self.create_dummy(DummyType.CABA_CLUB_SCORE_PLAYER_DATA, uid=self.__player.id, point=200)
        # 設定する称号.
        self.__titlemaster = self.create_dummy(DummyType.TITLE_MASTER, cost=100, days=1)
        # 称号情報.
        self.create_dummy(DummyType.TITLE_PLAYER_DATA, uid=self.__player.id)
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def get_urlargs(self):
        return '/%s' % self.__titlemaster.id
    
    def check(self):
        titleplayerdata = TitlePlayerData.getByKey(self.__player.id)
        if titleplayerdata.title != self.__titlemaster.id:
            raise AppTestError(u'称号が正しく設定されていません')
        elif (titleplayerdata.stime + datetime.timedelta(days=self.__titlemaster.days)) < OSAUtil.get_now():
            raise AppTestError(u'称号の期限が切れています')
