# -*- coding: utf-8 -*-
from platinumegg.test.base import ApiTestBase, AppTestError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.test.dummy_factory import DummyType
from platinumegg.app.cabaret.util.scout import ScoutDropItemData
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerRequest

class ApiTest(ApiTestBase):
    """レイド履歴一覧.
    """
    def setUp(self):
        TABLE = (
            (Defines.HappeningState.END, False),
            (Defines.HappeningState.MISS, False),
            (Defines.HappeningState.CANCEL, False),
            (Defines.HappeningState.END, True),
            (Defines.HappeningState.MISS, True),
        )
        NUM = Defines.RAIDLOG_CONTENT_NUM_PER_PAGE * 2
        
        # Player.
        player0 = self.create_dummy(DummyType.PLAYER)
        player0.friendlimit = NUM
        model_mgr = ModelRequestMgr()
        model_mgr.set_save(player0.getModel(PlayerFriend))
        model_mgr.write_all()
        model_mgr.write_end()
        
        # 履歴.
        for i in xrange(NUM):
            args = TABLE[i % len(TABLE)]
            self.createRaidLog(player0, *args)
        
        self.__player0 = player0
    
    def createRaidLog(self, player0, happeningstate, is_help):
        """履歴作成.
        """
        player1 = self.create_dummy(DummyType.PLAYER)
        
        if is_help:
            owner = player1
            friend = player0
        else:
            owner = player0
            friend = player1
        
        # アイテム.
        itemmaster = self.create_dummy(DummyType.ITEM_MASTER)
        data = ScoutDropItemData.create(Defines.ItemType.ITEM, itemmaster.id, filters={'ptype':Defines.CharacterType.TYPE_001}, rate=10000)
        items = [data.get_dropitem_dict()]
        
        # 報酬.
        prize = self.create_dummy(DummyType.PRIZE_MASTER, gold=100, gachapt=10, item=itemmaster)
        
        # レイドマスター.
        raidmaster = self.create_dummy(DummyType.RAID_MASTER, hp=1, prizes=[prize.id], helpprizes=[prize.id], cabaretking=100, demiworld=10)
        
        # ハプニング.
        happeningmaster = self.create_dummy(DummyType.HAPPENING_MASTER, raidmaster.id, items=items)
        
        # ハプニング情報.
        happening = self.create_dummy(DummyType.HAPPENING, owner.id, happeningmaster.id,  progress=happeningmaster.execution)
        
        # レイド.
        raidboss = self.create_dummy(DummyType.RAID, owner, happeningmaster, happening)
        raidboss.addDamageRecord(owner.id, 1)
        raidboss.refrectDamageRecord()
        raidboss.raid.save()
        
        # 救援.
        def addRequest(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friendrequest(model_mgr, v_player, o_player)
            model_mgr.write_all()
            model_mgr.write_end()
        
        def addFriend(v_player, o_player):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_add_friend(model_mgr, v_player.id, o_player.id)
            model_mgr.write_all()
            model_mgr.write_end()
        
        addRequest(owner, friend)
        addFriend(friend, owner)
        
        if happeningstate == Defines.HappeningState.CANCEL:
            model_mgr = ModelRequestMgr()
            BackendApi.tr_happening_cancel(model_mgr, owner, happeningmaster)
            model_mgr.write_all()
            model_mgr.write_end()
        else:
            model_mgr = ModelRequestMgr()
            BackendApi.tr_send_raidhelp(model_mgr, owner.id)
            model_mgr.write_all()
            model_mgr.write_end()
            
            raidboss.addDamageRecord(friend.id, 1)
            raidboss.refrectDamageRecord()
            raidboss.raid.save()
            
            if happeningstate == Defines.HappeningState.END:
                if is_help:
                    attacker = friend
                    helper = owner
                else:
                    attacker = owner
                    helper = friend
                
                deck = BackendApi.get_deck(attacker.id)
                deckcardlist = BackendApi.get_cards(deck.to_array())
                friendcard = BackendApi.get_leaders([helper.id]).get(helper.id)
                
                model_mgr = ModelRequestMgr()
                playerrequest = model_mgr.get_model(PlayerRequest, attacker.id)
                attacker.setModel(playerrequest)
                BackendApi.tr_raidbattle(model_mgr, raidboss.id, attacker.req_confirmkey, attacker, raidmaster, deckcardlist, friendcard, False)
                model_mgr.write_all()
                model_mgr.write_end()
                
            elif happeningstate == Defines.HappeningState.MISS:
                model_mgr = ModelRequestMgr()
                happening.etime = OSAUtil.get_now()
                model_mgr.set_save(happening)
                model_mgr.write_all()
                model_mgr.write_end()
                
                model_mgr = ModelRequestMgr()
                BackendApi.tr_happening_missed(model_mgr, happening.id)
                model_mgr.write_all()
                model_mgr.write_end()
        
        raidlog = BackendApi.get_raidlog_by_raidid(model_mgr, player0.id, happening.id)
        return raidlog
    
    def get_query_params(self):
        return {
            OSAUtil.KEY_OWNER_ID:self.__player0.dmmid,
        }
    
    def check(self):
        keys = (
            'raidloglist',
#            'url_page_next',
            'cur_page',
            'page_max',
        )
        for k in keys:
            if self.response.get(k, None) is None:
                raise AppTestError(u'%sが設定されていない' % k)
