# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """キャスト名鑑.
    """
    def setUp(self):
        # DMMID.
        self.__player = self.create_dummy(DummyType.PLAYER)
        
        for _ in xrange(Defines.ALBUM_PAGE_CONTENT_NUM + 1):
            cardmaster = self.create_dummy(DummyType.CARD_MASTER, rare=Defines.Rarity.NORMAL)
            self.create_dummy(DummyType.CARD, self.__player, cardmaster)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player.dmmid,
        }
    
    def check(self):
        keys = (
            'album_list',
            'cur_page',
            'page_max',
            'ctype',
            'rare',
            'url_post',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
