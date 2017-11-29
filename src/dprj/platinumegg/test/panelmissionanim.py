# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines

class ApiTest(ApiTestBase):
    """パネルミッション達成演出.
    """
    def setUp(self):
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # カード.
        cardmaster = self.create_dummy(DummyType.CARD_MASTER)
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, card=cardmaster)
        prizes = [prize.id]
        
        # パネル.
        self.__panelmaster = self.create_dummy(DummyType.PANEL_MISSION_PANEL_MASTER, prizes=prizes)
        
        missiondata_dict = {}
        for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
            # ミッション.
            self.create_dummy(DummyType.PANEL_MISSION_MISSION_MASTER, self.__panelmaster.id, number, prizes=prizes, condition_type=number, condition_value1=number, condition_value2=number)
            
            # 達成度.
            missiondata_dict[number] = {
                'cnt' : number,
                'etime' : OSAUtil.get_now() if number % 2 == 0 else OSAUtil.get_datetime_max(),
                'rtime' : OSAUtil.get_now() if number % 2 == 0 else OSAUtil.get_datetime_max(),
            }
        
        self.__panelmission_player = self.create_dummy(DummyType.PLAYER_PANEL_MISSION, self.__player0.id, self.__panelmaster.id)
        self.__panelmission_data = self.create_dummy(DummyType.PANEL_MISSION_DATA, self.__player0.id, self.__panelmaster.id, missiondata_dict=missiondata_dict)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%s' % (self.__panelmaster.id)
    
    def check(self):
        keys = (
            'redirect_url',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
