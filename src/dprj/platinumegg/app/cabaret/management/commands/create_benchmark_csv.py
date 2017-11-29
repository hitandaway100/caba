# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import settings_sub
from platinumegg.app.cabaret.util.model_csv import ModelCSVManager
import os
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Item import ItemMaster, Item
from platinumegg.app.cabaret.models.Card import CardMaster, Card, Deck,\
    CardAcquisition, AlbumAcquisition
from platinumegg.app.cabaret.models.Happening import HappeningMaster, Happening,\
    Raid, RaidLog
from platinumegg.app.cabaret.models.Player import Player, PlayerRegist,\
    PlayerTutorial, PlayerLogin, PlayerCard, PlayerExp, PlayerGold, PlayerFriend,\
    PlayerAp, PlayerDeck, PlayerGachaPt, PlayerScout, PlayerRequest,\
    PlayerTreasure, PlayerHappening, PlayerKey
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.player import ModelPlayer
from defines import Defines
from platinumegg.app.cabaret.models.PlayerLevelExp import PlayerLevelExpMaster
from platinumegg.app.cabaret.models.Area import AreaMaster, AreaPlayData
from platinumegg.app.cabaret.models.Scout import ScoutMaster, ScoutPlayData
from platinumegg.app.cabaret.util.api import BackendApi
import random
from platinumegg.app.cabaret.models.Friend import Friend
from platinumegg.app.cabaret.util.happening import RaidBoss, HappeningRaidSet,\
    HappeningSet
from platinumegg.app.cabaret.util.playerlog import ScoutClearLog, BossWinLog
from platinumegg.app.cabaret.models.Greet import GreetLog
from platinumegg.app.cabaret.models.Treasure import TreasureGoldMaster,\
    TreasureBronzeMaster, TreasureSilverMaster, TreasureGold, TreasureBronze,\
    TreasureSilver


class Command(BaseCommand):
    """負荷テスト用のユーザーデータのCSVを作成する.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'create_benchmark_csv'
        print '================================'
        
        
        USER_ID_START = OSAUtil.BENCH_USER_ID_START
        USER_NUM = 0
        if args:
            USER_NUM = int(args[0])
        USER_NUM = max(OSAUtil.BENCH_USER_ID_NUM, USER_NUM)
        
        print '================================'
        print 'USER_NUM=%d' % USER_NUM
        
        LEVEL = 1
        GOLD = 100000
        GACHA_PT = 3000
        CARD_NUM = 100
        CARD_LIMIT = CARD_NUM + 50
        FRIEND = 50
        FRIEND_REQUEST = 50
        FRIEND_EMPTY = 50
        FRIENDLIMIT = FRIEND + FRIEND_REQUEST * 2 + FRIEND_EMPTY
        RAID_ENDTIME = DateTimeUtil.strToDateTime("20150101", "%Y%m%d")
        RAIDLOG = 100
        GREETLOG = 100
        PRESENT = int(100 / len(Defines.ItemType.PRESENT_TYPES.keys()))
        PRESENT_LIMITTIME = DateTimeUtil.strToDateTime("20150101", "%Y%m%d")
        ITEM_RNUM = 50
        ITEM_VNUM = 50
        DECK_CAPACITY = 1000000
        CABARET_TREASURE = 100000
        
        TREASURE_NUM = 20
        
        OUTPUT_DIR = os.path.join(settings_sub.TMP_DOC_ROOT, 'dummy')
        csvmgr = ModelCSVManager(OUTPUT_DIR)
        
        model_mgr = ModelRequestMgr()
        
        # 各種マスターデータ.
        levelexpmaster = model_mgr.get_model(PlayerLevelExpMaster, LEVEL)
        item_all = model_mgr.get_mastermodel_all(ItemMaster)
        card_all = [master for master in model_mgr.get_mastermodel_all(CardMaster) if master.ckind == Defines.CardKind.NORMAL and master.hklevel == 1]
        happeningall = model_mgr.get_mastermodel_all(HappeningMaster)
        arealist = model_mgr.get_mastermodel_all(AreaMaster, order_by='id')[:2]
        scoutlist = ScoutMaster.fetchValues(filters={'area__in':[area.id for area in arealist]}, order_by='id')
        treasure_gold_all = model_mgr.get_mastermodel_all(TreasureGoldMaster)
        treasure_silver_all = model_mgr.get_mastermodel_all(TreasureSilverMaster)
        treasure_bronze_all = model_mgr.get_mastermodel_all(TreasureBronzeMaster)
        
        now = OSAUtil.get_now()
        
        print '================================'
        print 'players..'
        
        class ModelList:
            def __init__(self):
                self.modellist_all = []
            
            def add(self, modellist):
                csvmgr.setModelList(modellist)
        
        modellist_all = ModelList()
        
        for i in xrange(USER_NUM):
            modellist = []
            
            uid = i + USER_ID_START
            
            # プレイヤー作成.
            player = self.install(uid)
            
            # タイプ決定とか.
            self.regist(player, levelexpmaster, GOLD, GACHA_PT, FRIENDLIMIT, CARD_LIMIT, DECK_CAPACITY, CABARET_TREASURE)
            
            modellist.append(player.getModel(Player))
            for model_cls in ModelPlayer.Meta.MODELS:
                p = player.getModel(model_cls)
                if p:
                    modellist.append(p)
            
            # スカウト完了.
            for scout in scoutlist:
                playdata = ScoutPlayData.makeInstance(ScoutPlayData.makeID(uid, scout.id))
                playdata.progress = scout.execution
                modellist.append(playdata)
                
                # フレンドの近況.
                logdata = ScoutClearLog.makeData(player.id, scout.id)
                modellist.append(logdata)
            
            for area in arealist:
                model = AreaPlayData.makeInstance(AreaPlayData.makeID(uid, area.id))
                model.clevel = levelexpmaster.level
                modellist.append(model)
                
                # フレンドの近況.
                logdata = BossWinLog.makeData(player.id, area.id)
                modellist.append(logdata)
            
            # カード付与.
            playercard = player.getModel(PlayerCard)
            cardidlist = []
            for _ in xrange(CARD_NUM):
                playercard.card += 1
                cardid = Card.makeID(uid, playercard.card)
                
                cardmaster = random.choice(card_all)
                card = BackendApi.create_card_by_master(cardmaster)
                card.id = cardid
                card.uid = uid
                modellist.append(card)
                
                cardidlist.append(cardid)
            
            # デッキ設定.
            deck = Deck()
            deck.id = uid
            deck.set_from_array(cardidlist[:Defines.DECK_CARD_NUM_MAX])
            modellist.append(deck)
            
            # カード獲得フラグ.
            for cardmaster in card_all:
                cardacquisition = CardAcquisition.makeInstance(CardAcquisition.makeID(uid, cardmaster.id))
                cardacquisition.maxlevel = cardmaster.maxlevel
                modellist.append(cardacquisition)
                
                albumacquisition = AlbumAcquisition.makeInstance(AlbumAcquisition.makeID(uid, cardmaster.album))
                modellist.append(albumacquisition)
            
            # アイテム.
            for itemmaster in item_all:
                item = Item.makeInstance(Item.makeID(uid, itemmaster.id))
                item.rnum = ITEM_RNUM
                item.vnum = ITEM_VNUM
                modellist.append(item)
            
            # レイド履歴.
            states = (Defines.HappeningState.END, Defines.HappeningState.MISS, Defines.HappeningState.CANCEL)
            for lognumber in xrange(RAIDLOG):
                happeningmaster = random.choice(happeningall)
                raidmaster = BackendApi.get_raid_master(model_mgr, happeningmaster.boss)
                self.putRaidLog(modellist, player, happeningmaster, raidmaster, states[lognumber % len(states)])
            
            # レイド.
            happeningmaster = random.choice(happeningall)
            raidmaster = BackendApi.get_raid_master(model_mgr, happeningmaster.boss)
            self.putRaid(modellist, player, happeningmaster, raidmaster, RAID_ENDTIME)
            
            # プレゼント.
            def putPresent(itype, itemid, itemvalue):
                presentlist = BackendApi.create_present(model_mgr, 0, uid, itype, itemid, itemvalue, Defines.TextMasterID.ACCESS_BONUS, PRESENT_LIMITTIME, do_set_save=False)
                modellist.extend(presentlist)
                presentlist = BackendApi.create_present(model_mgr, 0, uid, itype, itemid, itemvalue, Defines.TextMasterID.ACCESS_BONUS, now, do_set_save=False)
                modellist.extend(presentlist)
            
            for _ in xrange(PRESENT):
                putPresent(Defines.ItemType.GOLD, 0, 1000)
                putPresent(Defines.ItemType.GACHA_PT, 0, 10)
                putPresent(Defines.ItemType.ITEM, random.choice(item_all).id, 1)
                putPresent(Defines.ItemType.CARD, random.choice(card_all).id, 1)
                putPresent(Defines.ItemType.RAREOVERTICKET, 0, 1)
                putPresent(Defines.ItemType.TRYLUCKTICKET, 0, 1)
                putPresent(Defines.ItemType.MEMORIESTICKET, 0, 1)
                putPresent(Defines.ItemType.GACHATICKET, 0, 1)
                putPresent(Defines.ItemType.GOLDKEY, 0, 1)
                putPresent(Defines.ItemType.SILVERKEY, 0, 1)
            
            # 宝箱.
            def makeTreasure(masterlist, model_cls, etime):
                master = random.choice(masterlist)
                model = model_cls()
                model.uid = uid
                model.mid = master.id
                model.etime = etime
                modellist.append(model)
            
            for _ in xrange(TREASURE_NUM):
                makeTreasure(treasure_gold_all, TreasureGold, now)
                makeTreasure(treasure_gold_all, TreasureGold, PRESENT_LIMITTIME)
                
                makeTreasure(treasure_silver_all, TreasureSilver, now)
                makeTreasure(treasure_silver_all, TreasureSilver, PRESENT_LIMITTIME)
                
                makeTreasure(treasure_bronze_all, TreasureBronze, now)
                makeTreasure(treasure_bronze_all, TreasureBronze, PRESENT_LIMITTIME)
            
            modellist_all.add(modellist)
            
            print 'complete uid=%d' % uid
        
        print '================================'
        print 'friends..'
        
        # ユーザーがそろっていないと作れないレコード.
        for i in xrange(USER_NUM):
            modellist = []
            
            uid = i + USER_ID_START
            
            # フレンド設定.
            self.putFriends(modellist, uid, USER_ID_START, USER_NUM, FRIEND, FRIEND_REQUEST)
            
            # あいさつ履歴.
            fid = uid
            for _ in xrange(GREETLOG):
                fid = ((fid - USER_ID_START + 1) % USER_NUM) + USER_ID_START
                while fid == uid:
                    fid = ((fid - USER_ID_START + 1) % USER_NUM) + USER_ID_START
                
                model = GreetLog()
                model.fromid = fid
                model.toid = uid
                modellist.append(model)
            
            modellist_all.add(modellist)
            
            print 'complete uid=%d' % uid
        
        csvmgr.output()
        
        print '================================'
        print 'all done..'
    
    def makeDmmId(self, uid):
        return '%s' % uid
    
    def putRaidLog(self, modellist, player, happeningmaster, raidmaster, state):
        """レイド.
        """
        etime = OSAUtil.get_now()
        happeningraidset = self.putRaid(modellist, player, happeningmaster, raidmaster, etime, state)
        
        raidlog = RaidLog()
        raidlog.uid = player.id
        raidlog.raidid = happeningraidset.happening.id
        raidlog.ctime = happeningraidset.happening.happening.ctime
        modellist.append(raidlog)
        
        return raidlog
    
    def putRaid(self, modellist, player, happeningmaster, raidmaster, etime, state=Defines.HappeningState.BOSS):
        """レイド.
        """
        
        playerhappening = player.getModel(PlayerHappening)
        playerhappening.happening += 1
        
        ins_id = Happening.makeID(playerhappening.id, playerhappening.happening)
        happening = Happening.makeInstance(ins_id)
        happening.oid = playerhappening.id
        happening.mid = happeningmaster.id
        happening.state = state
        happening.etime = etime
        happening.progress = happeningmaster.execution
        happening.gold = 0
        happening.items = {}
        happening.level = 1
        happening.hprate = random.randint(raidmaster.hprate_min, raidmaster.hprate_max)
        modellist.append(happening)
        
        if state in (Defines.HappeningState.BOSS, Defines.HappeningState.CLEAR, Defines.HappeningState.END, Defines.HappeningState.MISS):
            raid = Raid.makeInstance(happening.id)
            raid.oid = happening.oid
            raid.mid = raidmaster.id
            raid.level = happening.level
            raid.damage_record = {}
            
            raidboss = RaidBoss(raid, raidmaster)
            raid.hprate = happening.hprate
            if state in (Defines.HappeningState.CLEAR, Defines.HappeningState.END):
                raid.hp = 0
            else:
                raid.hp = raidboss.get_maxhp()
            raidboss.addDamageRecord(happening.oid, 1)
            raidboss.refrectDamageRecord()
            modellist.append(raid)
        else:
            raidboss = None
        
        return HappeningRaidSet(HappeningSet(happening, happeningmaster), raidboss)
    
    def putFriends(self, modellist, uid, uid_start, user_num_max, friend_num, friendrequest_num):
        """フレンド.
        """
        def makeId(number):
            fid = ((uid - uid_start + number + user_num_max) % user_num_max) + uid_start
            return fid
        
        def put(num, offset, state):
            for i in xrange(num):
                number = i + offset
                fid = makeId(number)
                ins = Friend.makeInstance(Friend.makeID(uid, fid))
                ins.state = state
                modellist.append(ins)
                
                if state == Defines.FriendState.ACCEPT:
                    ins = Friend.makeInstance(Friend.makeID(fid, uid))
                    ins.state = state
                    modellist.append(ins)
                elif state == Defines.FriendState.SEND:
                    ins = Friend.makeInstance(Friend.makeID(fid, uid))
                    ins.state = Defines.FriendState.RECEIVE
                    modellist.append(ins)
        
        # フレンド.
        offset = 1
        num = friend_num / 2
        put(num, offset, Defines.FriendState.ACCEPT)
        offset += num
        
        # フレンド申請.
        put(friendrequest_num, offset, Defines.FriendState.SEND)
    
    def regist(self, player, levelexpmaster, gold, gachapt, friendlimit, cardlimit, deckcapacity, cabaretking):
        """タイプ決定.
        """
        uid = player.id
        def setModel(model_cls, **kwargs):
            p = model_cls()
            p.id = uid
            for k,v in kwargs.items():
                setattr(p, k, v)
            player.setModel(p)
        
        setModel(PlayerRegist, ptype=Defines.CharacterType.TYPE_001)
        setModel(PlayerTutorial, tutorialstate=Defines.TutorialStatus.COMPLETED)
        setModel(PlayerLogin)
        setModel(PlayerCard)
        setModel(PlayerExp, exp=levelexpmaster.exp, level=levelexpmaster.level, hp=levelexpmaster.hp)
        setModel(PlayerGold, gold=gold)
        setModel(PlayerFriend, friendlimit=friendlimit)
        setModel(PlayerAp, apmax=levelexpmaster.ap)
        setModel(PlayerDeck, deckcapacitylv=levelexpmaster.deckcapacity, cardlimitlv=levelexpmaster.cardlimit, deckcapacityscout=deckcapacity, cardlimititem=cardlimit)
        setModel(PlayerGachaPt, gachapt=gachapt, rareoverticket=100, memoriesticket=100, tryluckticket=100)
        setModel(PlayerScout)
        setModel(PlayerRequest)
        setModel(PlayerTreasure, cabaretking=cabaretking, demiworld=cabaretking)
        setModel(PlayerHappening)
        setModel(PlayerKey)
    
    def install(self, uid):
        """初回アクセス.
        """
        p = Player()
        p.id = uid
        p.dmmid = self.makeDmmId(uid)
        player = ModelPlayer([p])
        return player
    
