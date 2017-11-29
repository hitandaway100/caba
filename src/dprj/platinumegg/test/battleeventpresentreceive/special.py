# -*- coding: utf-8 -*-
from platinumegg.test.base import AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.test.battleeventtestbase import BattleEventApiTestBase
from platinumegg.app.cabaret.util.api import BackendApi
import urllib
from platinumegg.app.cabaret.models.Player import PlayerRequest
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentData

class ApiTest(BattleEventApiTestBase):
    """バトルイベント贈り物受け取り(次を特別に選ぶ).
    """
    def setUp2(self):
        model_mgr = ModelRequestMgr()
        
        # Player.
        self.__player0 = self.create_dummy(DummyType.PLAYER)
        
        # イベントマスター.
        eventmaster = self.setUpEvent(model_mgr=model_mgr)
        self.__eventmaster = eventmaster
        
        # ランクのマスター.
        eventrankmaster = self.createRankMaster()
        self.__eventrankmaster = eventrankmaster
        
        # オープニングを閲覧済みに.
        self.setOpeningViewTime(self.__player0.id)
        
        # 参加させておく.
        self.joinRank(self.__player0.id)
        
        # 参加させておく.
        self.setLoginBonusReceived(self.__player0.id)
        
        # 贈り物マスター.
        self.__presentmaster = self.makePresentMaster(eventmaster.id, 1, point=100)
        special_conditions = [
            {
                'num' : self.__presentmaster.number,   # 5回でたら必ず出現.
                'cnt' : 5,
            }
        ]
        self.__special_presentmaster = self.makePresentMaster(eventmaster.id, 2, point=100, rate=0, special_conditions=special_conditions)
        
        # 贈り物のユーザ情報.
        self.__presentdata = self.makePresentData(self.__player0.id, eventmaster.id, point=self.__presentmaster.point, cur_presentmaster=self.__presentmaster)
        
        # 贈り物出現回数.
        self.makePresentCount(self.__presentmaster, self.__player0.id, 5)
        
        # プレゼント所持数.
        self.__present_num = BackendApi.get_present_num(self.__player0.id)
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def get_urlargs(self):
        return '/%s' % urllib.quote(self.__player0.req_confirmkey, '')
    
    def check(self):
        keys = (
            'redirect_url',
        )
        for k in keys:
            if not self.response.has_key(k):
                raise AppTestError(u'%sが設定されていない')
        
        # 鍵の更新確認.
        playerrequest = PlayerRequest.getByKey(self.__player0.id)
        if playerrequest.req_confirmkey == self.__player0.req_confirmkey:
            raise AppTestError(u'鍵が更新されていない')
        elif playerrequest.req_alreadykey != self.__player0.req_confirmkey:
            raise AppTestError(u'使用済みの鍵が更新されていない')
        
        # プレゼント数確認.
        if BackendApi.get_present_num(self.__player0.id) == self.__present_num:
            raise AppTestError(u'報酬が付与されていない')
        
        # ポイントのリセット確認.
        userdata = BattleEventPresentData.getByKey(BattleEventPresentData.makeID(self.__player0.id, self.__eventmaster.id))
        if 0 < userdata.point:
            raise AppTestError(u'ポイントがリセットされていない')
        
        # 贈り物設定確認.
        data = userdata.getData()
        if data is None:
            raise AppTestError(u'次の贈り物を設定していない')
        elif data['number'] != self.__special_presentmaster.number:
            raise AppTestError(u'次の贈り物が特別な贈り物になっていない')
        
        org_data = self.__presentdata.getData()
        data = userdata.getPreData()
        if data is None:
            raise AppTestError(u'前回の結果が設定されていない')
        elif data['number'] != org_data['number'] or data['content'] != org_data['content']:
            raise AppTestError(u'前回の結果の内容が想定外です')
        
