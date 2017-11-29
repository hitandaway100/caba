# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.util.promotion import PromotionSettings

class ApiTest(ApiTestBase):
    """クロスプロモーション達成確認.
    """
    
    def setUp(self):
        
        self.__player = self.create_dummy(DummyType.PLAYER)
        self.__player.level = 4
        self.__player.getModel(PlayerExp).save()
        
        self.create_dummy(DummyType.PROMOTION_CONFIG_KOIHIME)
        
        NUM = 8
        masterlist = []
        flags = {}
        for i in xrange(NUM):
            master = self.create_dummy(DummyType.PROMOTION_REQUIREMENT_MASTER_KOIHIME, condition_value=(i+1))
            masterlist.append(master)
            flags[master.id] = u'true' if master.condition_value <= self.__player.level else 'false'
        
        self.__masterlist = masterlist
        self.__flags = flags
    
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return '/%s/%s/%s/' % (PromotionSettings.Apps.KOIHIME, self.__player.dmmid, ','.join([str(master.id) for master in self.__masterlist]))
    
    def check(self):
        for master in self.__masterlist:
            if self.__flags[master.id] != self.response.get(str(master.id)):
                raise AppTestError(u'フラグが一致しません:id=%s' % master.id)
