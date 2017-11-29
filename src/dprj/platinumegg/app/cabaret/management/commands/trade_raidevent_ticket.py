# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventScore
from platinumegg.app.cabaret.models.Text import TextMaster
import settings
from django.db.models import Max
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.models.Present import Present
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold,\
    PlayerGachaPt, PlayerKey

class Command(BaseCommand):
    """レイドイベントのチケット換金.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'trade_raidevent_ticket'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        now = OSAUtil.get_now()
        
        config = BackendApi.get_current_raideventconfig(model_mgr)
        if now <= config.ticket_endtime:
            print u'秘宝交換とガチャ公開が終わっていません'
            return
        
        mid = config.mid
        
        eventmaster = BackendApi.get_raideventmaster(model_mgr, mid)
        if eventmaster is None:
            print u'イベントが設定されていません'
            return
        print 'check eventmaster...OK'
        
        # イベント設定.
        if now < config.endtime:
            print u'イベントがまだ終了していません'
            return
        print 'check event endtime...OK'
        
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        print '================================'
        print 'present text..'
        # 報酬文言.
        text = u'%sを交換しました' % eventmaster.ticketname
        print 'text:%s' % text
        
        # イケてない検索だけど.
        textmaster = TextMaster.getValues(filters={'text':text})
        if textmaster is None:
            def tr():
                idmax = TextMaster.all().aggregate(Max('id')).get('id__max')
                model_mgr = ModelRequestMgr()
                ins = TextMaster()
                ins.id = max(Defines.TextMasterID.AUTO_CREATION_ID_MIN, idmax + 1)
                ins.text = text
                model_mgr.set_save(ins)
                
                def writeEnd():
                    model_mgr.get_mastermodel_all(TextMaster, fetch_deleted=True, using=settings.DB_DEFAULT, reflesh=True)
                model_mgr.add_write_end_method(writeEnd)
                model_mgr.write_all()
                
                return model_mgr, ins
            tmp_model_mgr, textmaster = db_util.run_in_transaction(tr)
            tmp_model_mgr.write_end()
            message_id = textmaster.id
            print 'create!!'
        else:
            message_id = textmaster.id
        
        print 'present text id=%s' % message_id
        
        print '================================'
        print 'present receive:start'
        # プレゼントにあるチケットも換金.
        present_ctime_min = config.starttime
        present_ctime_max = max(config.endtime, config.ticket_endtime)
        LIMIT = 500
        
        filters = {
            'ctime__gte' : present_ctime_min,
            'ctime__lte' : present_ctime_max,
            'itype' : Defines.ItemType.EVENT_GACHATICKET,
        }
        def tr_receive(presentid, uid):
            model_mgr = ModelRequestMgr()
            player = BackendApi.get_players(None, [uid], [PlayerDeck, PlayerGold, PlayerGachaPt, PlayerKey], model_mgr=model_mgr)[0]
            BackendApi.tr_receive_present(model_mgr, player, [presentid], [])
            model_mgr.write_all()
            return model_mgr
        
        while True:
            presentlist = Present.fetchValues(['id', 'toid'], filters=filters, order_by='id', limit=LIMIT, offset=0)
            
            for present in presentlist:
                try:
                    db_util.run_in_transaction(tr_receive, present.id, present.toid).write_end()
                    print 'present receive id=%s' % present.id
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        print 'already received id=%s' % present.id
                    else:
                        raise
            
            if len(presentlist) < LIMIT:
                break
        
        print '================================'
        print 'trade:start'
        offset = 0
        LIMIT = 500
        
        GOLD = 1000
        
        filters = {
            'mid' : eventmaster.id,
        }
        
        def tr_trade(raideventscore_id):
            model_mgr = ModelRequestMgr()
            raideventscore = RaidEventScore.getByKeyForUpdate(raideventscore_id)
            ticket = raideventscore.ticket
            if ticket < 1:
                raise CabaretError('zero', CabaretError.Code.ALREADY_RECEIVED)
            
            # キャバゴールドを配布.
            prize = PrizeData.create(gold=ticket*GOLD)
            BackendApi.tr_add_prize(model_mgr, raideventscore.uid, [prize], message_id)
            
            # チケットを0に.
            raideventscore.ticket = 0
            model_mgr.set_save(raideventscore)
            
            model_mgr.write_all()
            
            return model_mgr, prize.gold
        
        while True:
            raideventscorelist = RaidEventScore.fetchValues(fields=['id', 'uid', 'ticket'], filters=filters, order_by='id', limit=LIMIT, offset=offset)
            offset += LIMIT
            
            for raideventscore in raideventscorelist:
                if raideventscore.ticket < 1:
                    print '%s: ticket zero!!' % raideventscore.uid
                    continue
                
                try:
                    model_mgr, gold = db_util.run_in_transaction(tr_trade, raideventscore.id)
                    model_mgr.write_end()
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        print '%s: ticket zero!!' % raideventscore.uid
                        continue
                    else:
                        raise
                print '%s:ticket %s=> gold %s' % (raideventscore.uid, raideventscore.ticket, gold)
            
            if len(raideventscorelist) < LIMIT:
                break
        
        print '================================'
        print 'all done..'
