# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from defines import Defines
import datetime

class ApiTest(ApiTestBase):
    """パネルミッション達成演出パラメータ(全ミッション達成).
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
        self.__panelmaster_next = self.create_dummy(DummyType.PANEL_MISSION_PANEL_MASTER, prizes=prizes)
        
        missiondata_dict = {}
        now = OSAUtil.get_now()
        yesterday = now - datetime.timedelta(days=1)
        for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
            # ミッション.
            self.create_dummy(DummyType.PANEL_MISSION_MISSION_MASTER, self.__panelmaster.id, number, prizes=prizes, condition_type=number, condition_value1=number, condition_value2=number)
            self.create_dummy(DummyType.PANEL_MISSION_MISSION_MASTER, self.__panelmaster_next.id, number, prizes=prizes, condition_type=number, condition_value1=number, condition_value2=number)
            
            # 達成度.
            etime = now
            if number % 2 == 0:
                etime = yesterday
            
            missiondata_dict[number] = {
                'cnt' : number,
                'etime' : etime,
                'rtime' : etime,
            }
        self.__now = now
        
        self.__panelmission_player = self.create_dummy(DummyType.PLAYER_PANEL_MISSION, self.__player0.id, self.__panelmaster_next.id)
        self.__panelmission_data = self.create_dummy(DummyType.PANEL_MISSION_DATA, self.__player0.id, self.__panelmaster.id, missiondata_dict=missiondata_dict)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/panelmission/%s' % (self.__panelmaster.id)
    
    def check(self):
        keys = (
            'logoPre',
            'pre',
            'bg',
            'clear',
            'panel',
            'card',
            'cname',
            'next0',
            'next1',
            'next2',
            'next3',
            'next4',
            'next5',
            'next6',
            'next7',
            'next8',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
        
        if self.response['panel'] != self.__panelmaster.id:
            raise AppTestError(u'現在のパネル番号が違う')
        
        tmp_clearlist = []
        for number in xrange(1, Defines.PANELMISSION_MISSIN_NUM_PER_PANEL+1):
            data = self.__panelmission_data.get_data(number)
            img = self.response.get('m%s' % (number - 1))
            name = self.response.get('mtext%s' % (number - 1))
            if data['rtime'] == self.__now:
                tmp_clearlist.append(str(number - 1))
            elif data['rtime'] < self.__now:
                if img is not None or name is not None:
                    raise AppTestError(u'達成済みなのにミッションが設定されている')
            else:
                if img is None or name is None:
                    raise AppTestError(u'達成いていないのにミッションが設定されていない')
        
        clearlist = self.response.get('clear').split(',')
        if len(set(tmp_clearlist) & set(clearlist)) != len(clearlist):
            raise AppTestError(u'今回達成したミッションが一致しない')
    
    
