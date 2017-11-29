# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
from platinumegg.test.cabaclubtestpage import CabaclubTest
from platinumegg.app.cabaret.models.CabaretClub import CabaClubCastPlayerData

class ApiTest(CabaclubTest):
    """キャバクラ店舗配置キャスト変更.
    """
    
    def setUp(self):
        ua_type = Defines.CabaClubEventUAType.LIVEN_UP
        # ユーザーを用意.
        self.__player = self.create_dummy(DummyType.PLAYER)
        # 店舗を用意.
        cabaclub_dummy = self.setUpCabaclub(self.__player)
        self.__cabaclub_dummy = cabaclub_dummy
        self.__storemaster = cabaclub_dummy.stores[ua_type]
        # キャストを配置しておく.
        self.__cardidlist = [card.id for card in cabaclub_dummy.cardlist]
        self.create_dummy(DummyType.CABA_CLUB_CAST_PLAYER_DATA, self.__player.id, self.__storemaster.id, cabaclub_dummy.cardlist[:-1])
    
    def get_query_params(self):
        params = {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
        return params
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return u'/%d/%d/%d' % (self.__storemaster.id, self.__cardidlist[0], self.__cardidlist[-1])
    
    def check(self):
        castdata = CabaClubCastPlayerData.getByKey(CabaClubCastPlayerData.makeID(self.__player.id, self.__storemaster.id))
        if len(castdata.cast) != len(set(castdata.cast) | set(self.__cardidlist[1:])):
            raise AppTestError(u'キャストが正しく配置されていません')
