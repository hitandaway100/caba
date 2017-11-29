# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from django.core.exceptions import ValidationError
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster,\
    BattleEventRankMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.models.Battle import BattleRankMaster
from platinumegg.app.cabaret.models.Card import CardMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = BattleEventRankMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        eventid = AppModelChoiceField(BattleEventMaster, required=False, label=u'イベントマスターID')
        loginbonus_text = AppModelChoiceField(TextMaster, required=False, label=u'ログイン時の報酬文言')
        winprizes_text = AppModelChoiceField(TextMaster, required=False, label=u'勝利報酬文言')
        loseprizes_text = AppModelChoiceField(TextMaster, required=False, label=u'敗北報酬文言')
        rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'バトルPTランキング報酬文言')
        group_rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'グループ内ランキング報酬文言')
        cardid = AppModelChoiceField(CardMaster, required=False, label=u'キャスト')
        battlepointprize_text = AppModelChoiceField(TextMaster, required=False, label=u'バトルポイント達成報酬文言')
        
        def _valid_primary_key(self):
            eventid = int(self.cleaned_data.get('eventid'))
            rank = int(self.cleaned_data.get('rank'))
            if eventid <= 0:
                raise ValidationError(u'eventidは1以上を指定して下さい')
            elif rank <= 0:
                raise ValidationError(u'midは1以上を指定して下さい')
            return BattleEventRankMaster.makeID(eventid, rank)
    
    def setting_property(self):
        self.MODEL_LABEL = u'バトルイベントランク'
    
    def __valid_master(self, master):
        if not (1 <= master.rank <= 0xff):
            raise ModelEditValidError(u'ランクが不正です.battleevent=%d' % master.id)
        
        master.id = BattleEventRankMaster.makeID(master.eventid, master.rank)
        
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        if BackendApi.get_battleevent_master(model_mgr, master.eventid) is None:
            raise ModelEditValidError(u'存在しないイベントが設定されています.battleeventrank=%d' % master.id)
        
        self.checkPrize(master, master.loginbonus, u'ログイン時の報酬', 'battleeventrank')
        
        master.battlepointprizes = master.battlepointprizes or []
        if not isinstance(master.battlepointprizes, (dict, list)):
            raise ModelEditValidError(u'バトルポイント達成報酬のJsonが壊れています.battleeventrank=%d' % master.id)
        for prizeidlist in master.get_battlepointprizes().values():
            self.checkPrize(master, prizeidlist, u'バトルポイント達成報酬', 'battleeventrank')
        
        try:
            pointtable = dict(master.pointtable)
        except:
            raise ModelEditValidError(u'獲得名声PTのテーブルが壊れています.battleeventrank=%d' % master.id)
        
        for k,v in pointtable.items():
            if k != "default" and not isinstance(k, (int, long)):
                raise ModelEditValidError(u'名声PTのテーブルの順位に不正な値が設定されています.battleeventrank=%d' % master.id)
            elif not isinstance(v, (int, long)):
                raise ModelEditValidError(u'名声PTのテーブルの名声PTに数値以外が設定されています.battleeventrank=%d' % master.id)
        
        try:
            rankuptable = dict(master.rankuptable)
        except:
            raise ModelEditValidError(u'ランクアップテーブルが壊れています.battleeventrank=%d' % master.id)
        
        for k,v in rankuptable.items():
            if not isinstance(k, (int, long)):
                raise ModelEditValidError(u'ランクアップテーブルの順位に不正な値が設定されています.battleeventrank=%d' % master.id)
            elif not isinstance(v, (int, long)):
                raise ModelEditValidError(u'ランクアップテーブルの名声PTに数値以外が設定されています.battleeventrank=%d' % master.id)
        
        master.fevertable = master.fevertable or []
        try:
            fevertable = dict(master.fevertable)
        except:
            raise ModelEditValidError(u'フィーバー発生率テーブルが壊れています.battleeventrank=%d' % master.id)
        
        for k,v in fevertable.items():
            if not k in ("default", "worst") and not isinstance(k, (int, long)):
                raise ModelEditValidError(u'フィーバー発生率の順位に不正な値が設定されています.battleeventrank=%d' % master.id)
            elif not isinstance(v, (int, long)):
                raise ModelEditValidError(u'フィーバー発生率の発生率に数値以外が設定されています.battleeventrank=%d' % master.id)
        
        def checkBattlePrize(clumnprizes, name):
            datalist = []
            try:
                for v in clumnprizes:
                    data = BattleRankMaster.PrizeData(v)
                    if 0 < data.rate:
                        datalist.append(data)
                    
                    self.checkPrize(master, data.prizes, name, 'battleeventrank')
                
                if len(datalist) == 0:
                    raise ModelEditValidError(u'報酬が設定されていません.battleeventrank=%d' % master.id)
            except ModelEditValidError:
                raise
            except:
                raise ModelEditValidError(u'報酬データに問題があります.battleeventrank=%d' % master.id)
        checkBattlePrize(master.winprizes, u'勝利報酬')
        checkBattlePrize(master.loseprizes, u'敗北報酬')
        
        def checkRankingPrize(prizes, name):
            if not isinstance(prizes, list):
                raise ModelEditValidError(u'%sのJsonが壊れています.battleevent=%d' % (name, master.id))
            for data in prizes:
                diff = set(['prize','rank_min','rank_max']) - set(data.keys())
                if diff:
                    raise ModelEditValidError(u'%sに想定外のデータが含まれています.battleevent=%d' % (name, master.id))
                self.checkPrize(master, data['prize'], name, 'battleeventrank')
        checkRankingPrize(master.rankingprizes, u'バトルPTランキング報酬')
        checkRankingPrize(master.group_rankingprizes, u'グループ別ランキング報酬')
        
        if master.cardid:
            cardmaster = BackendApi.get_cardmasters([master.cardid], model_mgr).get(master.cardid)
            if not cardmaster:
                raise ModelEditValidError(u'存在しないキャストが設定されています.battleevent=%d' % master.id)
            elif master.name != cardmaster.name:
                raise ModelEditValidError(u'ランク名とキャスト名が一致しません.battleevent=%d' % master.id)
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        errors = []
        
        master_all = BattleEventRankMaster.fetchValues()
        master_all.sort(key=lambda x:((x.eventid<<32)+x.rank))
        
        eventid = None
        rank = 0
        rankmaster_map = {}
        for master in master_all:
            if eventid != master.eventid:
                eventid = master.eventid
                rank = 0
            
            if rank == master.rank:
                errors.append(u'重複:eventid=%d, rank=%d' % (eventid, rank))
            elif rank != (master.rank - 1):
                for st in xrange(rank+1, master.rank):
                    errors.append(u'不足:eventid=%d, rank=%d' % (eventid, st))
            rank = master.rank
            event_map = rankmaster_map[master.eventid] = rankmaster_map.get(master.eventid) or {}
            event_map[rank] = master
        
        for master in master_all:
            table = dict(master.rankuptable)
            event_map = rankmaster_map.get(master.eventid) or {}
            for grouprank, rankup in table.items():
                rank = master.rank + rankup
                if not event_map.get(rank):
                    errors.append(u'ランクアップ先が存在しない:eventid=%d, rank=%d, rankuptable_key=%s' % (eventid, master.rank, grouprank))
        
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
