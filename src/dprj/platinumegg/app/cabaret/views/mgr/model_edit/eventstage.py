# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    ModelEditValidError
from platinumegg.app.cabaret.util.scout import ScoutDropItemSelector,\
    ScoutHappeningSelector
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi


class EventStageHandler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    def valid_stagedata(self, master, eventmaster_cls):
        
        model_mgr = self.getModelMgr()
        
        eventmaster = model_mgr.get_model(eventmaster_cls, master.eventid)
        if eventmaster is None:
            raise ModelEditValidError(u'イベントが存在しません.stage=%d' % master.id)
        
        bossid = master.boss
        if bossid != 0:
            boss = BackendApi.get_boss(model_mgr, bossid)
            if boss is None:
                raise ModelEditValidError(u'存在しないボスが設定されています.stage=%d' % master.id)
        
        prizes = master.prizes
        if len(prizes) != len(list(set(prizes))):
            raise ModelEditValidError(u'報酬が重複しています.stage=%d' % master.id)
        
        prizelist = BackendApi.get_prizemaster_list(model_mgr, prizes)
        if len(prizes) != len(prizelist):
            raise ModelEditValidError(u'存在しない報酬が設定されています.stage=%d' % master.id)
        
        bossprizes = master.bossprizes
        if len(bossprizes) != len(list(set(bossprizes))):
            raise ModelEditValidError(u'ボス撃破報酬が重複しています.stage=%d' % master.id)
        
        bossprizelist = BackendApi.get_prizemaster_list(model_mgr, bossprizes)
        if len(bossprizes) != len(bossprizelist):
            raise ModelEditValidError(u'存在しないボス撃破報酬が設定されています.stage=%d' % master.id)
        
        earlybonus = BackendApi.get_prizemaster_list(model_mgr, master.earlybonus)
        if len(earlybonus) != len(master.earlybonus):
            raise ModelEditValidError(u'存在しない早期クリアボーナスが設定されています.stage=%d' % master.id)
        
        try:
            ScoutDropItemSelector(None, master, 0).validate()
            ScoutHappeningSelector(None, master).validate()
        except CabaretError, err:
            raise ModelEditValidError('%s, happening=%d' % (err.value, master.id))
    
    def valid_write_end(self):
        errors = []
        
        model_cls = self.Form.Meta.model
        master_all = model_cls.fetchValues()
        master_all.sort(key=lambda x:((x.eventid<<32)+x.stage))
        
        eventid = None
        area = 1
        stage = 0
        for master in master_all:
            if eventid != master.eventid:
                eventid = master.eventid
                area = 1
                stage = 0
            
            if master.area < area or (area+1) < master.area:
                errors.append(u'不正エリア:eventid=%d, stage=%d, area=%d' % (master.eventid, master.stage, master.area))
            else:
                area = master.area
            
            if stage == master.stage:
                errors.append(u'重複:eventid=%d, stage=%d' % (eventid, stage))
            elif stage != (master.stage - 1):
                for st in xrange(stage+1, master.stage):
                    errors.append(u'不足:eventid=%d, stage=%d' % (eventid, st))
            
            stage = master.stage
        
        if errors:
            raise ModelEditValidError('<br />'.join(errors))
