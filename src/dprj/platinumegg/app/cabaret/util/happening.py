# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import operator
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
import settings_sub
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventRaidMaster
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventRaidMaster
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventRaidMaster


class HappeningUtil:
    
    class EventTypes:
        (
            RAID,
            SCOUT,
            PRODUCE,
        ) = range(3)
    
    @staticmethod
    def makeThumbnailUrlIcon(master):
        """52*52サムネ画像.
        """
        return u'%s/Raid_icon.png' % master.thumb
    
    @staticmethod
    def makeThumbnailUrl(master, is_produceevent=False):
        """サムネ画像.
        """
        if is_produceevent:
            return HappeningUtil.makeProduceEventBossThumbnailUrl(master)
        return u'%s/Raid_boss.png' % master.thumb

    @staticmethod
    def makeProduceEventCastThumbnailUrl(eventmaster, order):
        return u'event/{produce_path}/boss/bosscast_{cast_order}.png'.format(produce_path=eventmaster.htmlname, cast_order=order)

    @staticmethod
    def makeProduceEventBossThumbnailUrl(master):
        """演出用：プロデュースイベントボスサヌネ画像
        """
        return u'%s.png' % master.thumb
    
    @staticmethod
    def __get_eventid(model_eventvalue, eventtype):
        return int(model_eventvalue & 0xffffffff) if int(model_eventvalue >> 32) == eventtype else 0
    
    @staticmethod
    def __make_eventvalue(eventtype, eventid):
        if eventid:
            return (eventtype << 32) + eventid
        else:
            return 0
    
    @staticmethod
    def __set_eventparams(happening, eventtype, eventid):
        happening.event = HappeningUtil.__make_eventvalue(eventtype, eventid)
    
    @staticmethod
    def get_raideventid(model_eventvalue):
        return HappeningUtil.__get_eventid(model_eventvalue, HappeningUtil.EventTypes.RAID)
    
    @staticmethod
    def make_raideventvalue(eventid):
        return HappeningUtil.__make_eventvalue(HappeningUtil.EventTypes.RAID, eventid)
    
    @staticmethod
    def set_raideventid(happening, eventid):
        HappeningUtil.__set_eventparams(happening, HappeningUtil.EventTypes.RAID, eventid)
    
    @staticmethod
    def get_scouteventid(model_eventvalue):
        return HappeningUtil.__get_eventid(model_eventvalue, HappeningUtil.EventTypes.SCOUT)
    
    @staticmethod
    def make_scouteventvalue(eventid):
        return HappeningUtil.__make_eventvalue(HappeningUtil.EventTypes.SCOUT, eventid)
    
    @staticmethod
    def set_scouteventid(happening, eventid):
        HappeningUtil.__set_eventparams(happening, HappeningUtil.EventTypes.SCOUT, eventid)

    @staticmethod
    def get_produceeventid(model_eventvalue):
        return HappeningUtil.__get_eventid(model_eventvalue, HappeningUtil.EventTypes.PRODUCE)

    @staticmethod
    def make_produceeventvalue(eventid):
        return HappeningUtil.__make_eventvalue(HappeningUtil.EventTypes.PRODUCE, eventid)

    @staticmethod
    def set_produceeventid(happening, eventid):
        HappeningUtil.__set_eventparams(happening, HappeningUtil.EventTypes.PRODUCE, eventid)

class HappeningSet():
    """ハプニング.
    """
    def __init__(self, happening, master):
        self.__happening = happening
        self.__master = master
    
    @property
    def id(self):
        return self.__happening.id
    
    @property
    def happening(self):
        return self.__happening
    @property
    def master(self):
        return self.__master

class RaidDamageRecord():
    """レイドのダメージ履歴.
    """
    def __init__(self, uid, damage=0, cnt=0, number=0, feverendtime=None, champagne=False, champagne_post=0, champagne_add=0, material=0, tanzaku=0, tanzaku_post=0):
        self.__uid = uid
        self.__damage = damage
        self.__damage_cnt = cnt
        self.__number = number
        if not feverendtime:
            feverendtime = OSAUtil.get_datetime_min()
        elif not isinstance(feverendtime, datetime.datetime):
            feverendtime = DateTimeUtil.strToDateTime(feverendtime)
        self.__feverendtime = feverendtime
        self.__champagne = bool(champagne)
        self.__champagne_post = champagne_post
        self.__champagne_add = champagne_add
        self.__material_num = material
        self.__tanzaku = tanzaku
        self.__tanzaku_post = tanzaku_post
    
    @property
    def uid(self):
        return self.__uid
    
    @property
    def damage(self):
        return self.__damage
    
    @property
    def damage_cnt(self):
        return self.__damage_cnt
    
    @property
    def number(self):
        return self.__number
    
    @property
    def feverendtime(self):
        return self.__feverendtime
    
    @property
    def champagne(self):
        return self.__champagne
    
    @property
    def champagne_num_add(self):
        return self.__champagne_add
    
    @property
    def champagne_num_post(self):
        return self.__champagne_post
    
    @property
    def champagne_num_pre(self):
        return self.champagne_num_post - self.champagne_num_add
    
    @property
    def material_num(self):
        return self.__material_num
    
    @property
    def tanzaku_num(self):
        return self.__tanzaku
    
    @property
    def tanzaku_num_post(self):
        return self.__tanzaku_post
    
    @property
    def tanzaku_num_pre(self):
        return self.tanzaku_num_post - self.tanzaku_num
    
    def addDamage(self, damage):
        self.__damage += damage
        self.__damage_cnt += 1
    
    def setNumber(self, number):
        self.__number = number
    
    def updateFeverTime(self, feverendtime):
        self.__feverendtime = feverendtime
    
    def is_fever(self, now=None):
        now = now or OSAUtil.get_now()
        return now < self.feverendtime
    
    def setChampagne(self, champagne):
        self.__champagne = bool(champagne)
    
    def setChampagneResult(self, champagne_num_post, champagne_num_add):
        self.__champagne_post = champagne_num_post
        self.__champagne_add = champagne_num_add
    
    def setMaterialResult(self, material_num):
        self.__material_num = material_num
    
    def setTanzakuResult(self, tanzaku, tanzaku_post):
        self.__tanzaku = tanzaku
        self.__tanzaku_post = tanzaku_post
    
    def to_dict(self):
        """DBへ保存するために辞書にする.
        keyはコンストラクタの引数の名前.
        """
        data = {
            'damage' : self.__damage,
            'cnt' : self.__damage_cnt,
            'number' : self.__number,
            'feverendtime' : DateTimeUtil.dateTimeToStr(self.__feverendtime),
        }
        if self.champagne:
            data['champagne'] = 1
        if self.champagne_num_add:
            data.update(champagne_post=self.champagne_num_post, champagne_add=self.champagne_num_add)
        if self.material_num:
            data['material'] = self.material_num
        if self.tanzaku_num:
            data.update(tanzaku=self.tanzaku_num, tanzaku_post=self.tanzaku_num_post)
        return data

class RaidBoss():
    """レイドボス.
    """
    # 協力者報酬が適用開始される時間.
    DEMIWORLD_OPEN_TIME = DateTimeUtil.strToDateTime("201402031600", "%Y%m%d%H%M")
    # HPが仕様変更される時間.
    if settings_sub.IS_DEV:
        HP_UPDATE_TIME = DateTimeUtil.strToDateTime("201402061430", "%Y%m%d%H%M")
    else:
        HP_UPDATE_TIME = DateTimeUtil.strToDateTime("201402071430", "%Y%m%d%H%M")
    
    # ダメージ履歴のバージョン.
    DAMAGE_RECORDVERSION = 1
    
    # レイドイベント報酬で通常のも受け取れるようになった時間.
    if settings_sub.IS_DEV:
        RAIDEVENT_PRIZE_UPDATETIME = DateTimeUtil.strToDateTime("201402261300", "%Y%m%d%H%M")
    else:
        RAIDEVENT_PRIZE_UPDATETIME = DateTimeUtil.strToDateTime("201402281500", "%Y%m%d%H%M")
    
    def __init__(self, raid, master, eventraidmaster=None):
        self.__raid = raid
        self.__master = master
        self.__eventraidmaster = None
        self.__records = {}
        self.__combo_cnt = 0
        self.__combo_etime = OSAUtil.get_datetime_min()
        self.setEventRaidMaster(eventraidmaster)
        
        combodata = self.__getDBComboData()
        if combodata:
            self.__combo_cnt = combodata['cnt']
            self.__combo_etime = combodata['etime']
        
    
    @property
    def id(self):
        return self.raid.id
    
    @property
    def raid(self):
        return self.__raid
    @property
    def master(self):
        return self.__master
    @property
    def raideventraidmaster(self):
        return self.__eventraidmaster if isinstance(self.__eventraidmaster, RaidEventRaidMaster) else None
    @property
    def scouteventraidmaster(self):
        return self.__eventraidmaster if isinstance(self.__eventraidmaster, ScoutEventRaidMaster) else None
    @property
    def produceeventraidmaster(self):
        return self.__eventraidmaster if isinstance(self.__eventraidmaster, ProduceEventRaidMaster) else None
    
    @property
    def hp(self):
        return self.raid.hp
    @property
    def defense(self):
        return self.get_defense()
    @property
    def ctype(self):
        return self.master.ctype
    @property
    def weakbonus(self):
        return self.master.weakbonus
    
    @property
    def timebonusflag(self):
        """タイムボーナスフラグ.
        """
        return self.raid.timebonusflag
    
    @property
    def fastflag(self):
        """秘宝ボーナスフラグ.
        """
        return self.raid.fastflag
    
    @property
    def combo_cnt(self):
        return self.__combo_cnt
    
    @property
    def combo_etime(self):
        return self.__combo_etime
    
    def __getDBDamageRecordData(self):
        """Raid.damage_recordの中身のバージョンを見て取得.
        """
        damage_record = self.raid.getDamageRecord()
        version = damage_record.get('VERSION', None)
        if version == 1:
            # コンボボーナス時間追加バージョン.
            records = damage_record['records'] = damage_record.get('records', {})
            return records
        else:
            # リリース時のバージョン.
            return damage_record
    
    def __getDBComboData(self):
        """コンボ情報を取得.
        """
        damage_record = self.raid.getDamageRecord()
        version = damage_record.get('VERSION', None)
        if version == 1:
            # コンボボーナス時間追加バージョン.
            return damage_record.get('combo')
        else:
            # リリース時のバージョン.
            return None
    
    def __saveDBDamageRecordData(self, records):
        """Raid.damage_recordの中身のバージョンをつけて保存.
        """
        self.raid.setDamageRecord({
            'VERSION' : RaidBoss.DAMAGE_RECORDVERSION,
            'records' : records,
            'combo' : {
                'cnt' : self.__combo_cnt,
                'etime' : self.__combo_etime or OSAUtil.get_now(),
            },
        })
    
    def setEventRaidMaster(self, eventraidmaster):
        if eventraidmaster and eventraidmaster.mid != self.master.id:
            raise CabaretError(u'不正な設定を行っている')
        self.__eventraidmaster = eventraidmaster
    
    def get_maxhp(self):
        """最大HP.
        """
        if (self.raid.ctime or OSAUtil.get_now()) < RaidBoss.HP_UPDATE_TIME:
            # 旧仕様.
            return max(1, (self.master.hpbase + self.raid.level * self.master.hpgrowth) * self.raid.hprate / 100)
        elif self.raideventraidmaster:
            lvband = max(0,int(self.raid.level/10-1))
            cnt = lvband*(lvband+1)/2
            pre = cnt*10 - lvband
            return max(1, (self.master.hpbase+pre*10*self.master.hpgrowth+self.master.hpgrowth*10*(self.raid.level-1)) * self.raid.hprate / 100)
        else:
            return max(1, (self.master.hpbase + self.raid.level * self.master.hpgrowth) * self.raid.hprate / 100)
    
    def get_defense(self):
        """防御力.
        """
        return self.master.defensebase + self.raid.level * self.master.defensegrowth
    
    def get_member_num(self):
        """参加人数.
        """
        cnt = 0
        for uid in self.getDamageRecordUserIdList():
            if 0 < self.getDamageRecord(uid).damage_cnt:
                cnt += 1
        return cnt
    
    def get_cabaretking(self):
        """キャバ王の秘宝.
        """
        return self.master.cabaretkingbase + self.raid.level * self.master.cabaretkinggrowth
    
    def get_demiworld(self):
        """キャバ王の秘宝(救援).
        """
        if self.raid.ctime < RaidBoss.DEMIWORLD_OPEN_TIME:
            # 公開前に発生したレイドについては0
            return 0
        else:
            return self.master.demiworldbase + self.raid.level * self.master.demiworldgrowth
    
    def get_owner_eventpoint(self):
        """発見者のイベントポイント.
        """
        point = 0
        if self.raideventraidmaster:
            if self.timebonusflag:
                point = self.raideventraidmaster.ownerpoint_timebonus + self.raid.level * self.raideventraidmaster.ownerpoint_timebonus_growth
            else:
                point = self.raideventraidmaster.ownerpoint + self.raid.level * self.raideventraidmaster.ownerpoint_growth
        return int(point * self.raid.evpointrate / 100)
    
    def get_mvp_eventpoint(self):
        """MVPのイベントポイント.
        """
        point = 0
        if self.raideventraidmaster:
            if self.timebonusflag:
                point = self.raideventraidmaster.mvppoint_timebonus + self.raid.level * self.raideventraidmaster.mvppoint_timebonus_growth
            else:
                point = self.raideventraidmaster.mvppoint + self.raid.level * self.raideventraidmaster.mvppoint_growth
        return int(point * self.raid.evpointrate / 100)
    
    def is_big(self):
        """大ボスフラグ.
        """
        return self.raideventraidmaster and self.raideventraidmaster.big

    def is_produceevent_bigboss(self):
        """プロデュースイベント大ボスフラグ
        """
        return self.produceeventraidmaster and self.produceeventraidmaster.big
    
    def getDamageRecordUserIdList(self):
        """ダメージ履歴にあるユーザーIDを取得.
        """
        damage_record = self.__getDBDamageRecordData()
        uidlist = list(set(list(self.__records.keys()) + list(damage_record.keys())))
        return uidlist
    
    def is_help_sent(self):
        """救援依頼を送ったか.
        """
        return 1 < len(self.getDamageRecordUserIdList())
    
    def getLastDamageRecord(self):
        """最後のダメージ履歴.
        """
        uidlist = self.getDamageRecordUserIdList()
        recordlist = [self.getDamageRecord(uid) for uid in uidlist]
        if recordlist:
            recordlist.sort(key=operator.attrgetter('number'), reverse=True)
            record = recordlist[0]
            if 0 < record.damage_cnt:
                return record
        return None
    
    def getDamageRecordList(self):
        """ダメージ履歴を全て取得.
        """
        uidlist = self.getDamageRecordUserIdList()
        recordlist = [self.getDamageRecord(uid) for uid in uidlist]
        recordlist.sort(key=operator.attrgetter('damage'), reverse=True)
        return recordlist
    
    def getDamageRecord(self, uid):
        """ダメージ履歴を取得.
        """
        if self.__records.has_key(uid):
            return self.__records[uid]
        damage_record = self.__getDBDamageRecordData()
        data = damage_record.get(uid, None)
        if data is None:
            record = RaidDamageRecord(uid)
        else:
            record = RaidDamageRecord(uid, **data)
        self.__records[uid] = record
        return record
    
    def addUser(self, uid):
        """ダメージ履歴に追記.
        """
        return self.getDamageRecord(uid)
    
    def addDamageRecord(self, uid, damage, feverendtime=None):
        """ダメージ履歴に追記.
        """
        lastrecord = self.getLastDamageRecord()
        if lastrecord:
            number = lastrecord.number + 1
        else:
            number = 1
        record = self.getDamageRecord(uid)
        record.addDamage(damage)
        record.setNumber(number)
        if feverendtime:
            record.updateFeverTime(feverendtime)
    
    def refrectDamageRecord(self):
        """ダメージ履歴の更新分を反映.
        """
        damage_record = self.__getDBDamageRecordData()
        for record in self.__records.values():
            damage_record[record.uid] = record.to_dict()
        self.__saveDBDamageRecordData(damage_record)
    
    def getMVPList(self):
        """MVPユーザIDを取得.
        """
        recordlist = self.getDamageRecordList()
        recordlist.sort(key=lambda x:x.damage, reverse=True)
        uidlist = []
        damage = 0
        for record in recordlist:
            if record.damage == 0 or record.damage < damage:
                break
            uidlist.append(record.uid)
            damage = record.damage
        return uidlist
    
    def getBorderDamageForPrizeGet(self):
        """報酬獲得に必要なダメージ.
        """
        if not self.raideventraidmaster:
            return 0
        maxhp = self.get_maxhp()
        border = int(maxhp * 3 / 100)
        return border
    
    def getHelpEventPoints(self, uid=None):
        """協力者のイベントポイント.
        ユーザIDがキー, ポイントが値.
        """
        data = {}
        if not self.raideventraidmaster:
            return data
        
        maxhp = self.get_maxhp()
        border = self.getBorderDamageForPrizeGet()
        
        if uid is None:
            recordlist = self.getDamageRecordList()
        else:
            recordlist = []
            record = self.getDamageRecord(uid)
            if record:
                recordlist.append(record)
        
        maxpoint = self.get_mvp_eventpoint()
        
        oid = self.raid.oid
        for record in recordlist:
            damage = record.damage
            if damage < border:
                continue
            elif record.uid == oid:
                continue
            # MVP報酬×貢献度（ボスに与えたダメージ割合）×5.
            data[record.uid] = int(min(maxpoint * damage * 5 / maxhp, maxpoint / 2))
        return data
    
    def getCurrentComboCount(self, now=None):
        """現在のコンボ数.
        """
        now = now or OSAUtil.get_now()
        if now < self.combo_etime:
            return self.combo_cnt
        else:
            return 0
    
    def setComboData(self, cnt, etime):
        """コンボ数を設定.
        """
        self.__combo_cnt = cnt
        self.__combo_etime = etime
    
    def addComboCount(self, uid, seconds, now=None, cnt=1):
        """コンボ数を加算.
        """
        now = now or OSAUtil.get_now()
        cur_cnt = self.getCurrentComboCount(now)
        if 0 < cur_cnt:
            lastrecord = self.getLastDamageRecord()
            if lastrecord and lastrecord.uid == uid:
                # 直前に同じ人が接客しているので加算しない.
                return
        self.setComboData(cur_cnt + cnt, now + datetime.timedelta(seconds=seconds))
    
    def get_tanzaku_number(self, uid):
        if self.scouteventraidmaster is None:
            return None
        elif uid == self.raid.oid:
            return self.scouteventraidmaster.tanzaku_number if self.scouteventraidmaster.tanzaku_rate else None
        else:
            return self.scouteventraidmaster.tanzaku_help_number if self.scouteventraidmaster.tanzaku_help_rate else None

class HappeningRaidSet():
    """ハプニングとレイド.
    """
    
    def __init__(self, happening, raidboss=None):
        self.__happening = happening
        self.__raidboss = None
        if raidboss:
            self.setRaidBoss(raidboss)
    
    @property
    def id(self):
        return self.__happening.id
    
    @property
    def happening(self):
        return self.__happening
    @property
    def raidboss(self):
        return self.__raidboss
    
    def setRaidBoss(self, raidboss):
        if raidboss.id != self.__happening.id:
            raise CabaretError(u'設定するレイドのIDが正しくありません')
        self.__raidboss = raidboss
