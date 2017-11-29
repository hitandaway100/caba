# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from django.core.exceptions import ValidationError
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import BattleEventPresentMaster,\
    BattleEventPresentContentMaster


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = BattleEventPresentMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'id',
            )
        eventid = AppModelChoiceField(BattleEventMaster, required=False, label=u'イベントマスターID')
        
        def _valid_primary_key(self):
            eventid = int(self.cleaned_data.get('eventid'))
            number = int(self.cleaned_data.get('number'))
            if eventid <= 0:
                raise ValidationError(u'eventidは1以上を指定して下さい')
            elif number <= 0:
                raise ValidationError(u'numberは1以上を指定して下さい')
            return BattleEventPresentMaster.makeID(eventid, number)
    
    def setting_property(self):
        self.MODEL_LABEL = u'バトルイベント贈り物'
    
    def __valid_master(self, master):
        master.id = BattleEventPresentMaster.makeID(master.eventid, master.number)
        if not master.is_public:
            return
        
        content_dict = None
        if isinstance(master.contents, list):
            try:
                content_dict = dict(master.contents)
            except:
                pass
        if content_dict is None:
            raise ModelEditValidError(u'中身の情報が壊れています.battleeventpresent:eventid=%d,number=%d' % (master.eventid, master.number))
        
        for v in content_dict.values():
            if not isinstance(v, (int, long)) or v < 1:
                raise ModelEditValidError(u'中身の情報に確率が設定されていません.battleeventpresent:eventid=%d,number=%d' % (master.eventid, master.number))
        
        contentidlist = content_dict.keys()
        if len(contentidlist) != len(master.contents):
            raise ModelEditValidError(u'中身の情報が重複しています.battleeventpresent:eventid=%d,number=%d' % (master.eventid, master.number))
        contentmasterlist = BattleEventPresentContentMaster.getByKey(contentidlist)
        if len(contentidlist) != len(contentmasterlist):
            raise ModelEditValidError(u'中身の情報が存在しません.battleeventpresent:eventid=%d,number=%d' % (master.eventid, master.number))
    
    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)
    
    def valid_write_end(self):
        errors = []
        
        master_all = BattleEventPresentMaster.fetchValues()
        master_all.sort(key=lambda x:x.id)
        
        eventid = None
        number = 0
        conditions = {}
        exists = {}
        
        for master in master_all:
            if eventid != master.eventid:
                eventid = master.eventid
                number = 0
            
            if number == master.number:
                errors.append(u'重複:eventid=%d, number=%d' % (eventid, number))
            elif number != (master.number - 1):
                for st in xrange(number+1, master.number):
                    errors.append(u'不足:eventid=%d, number=%d' % (eventid, st))
            number = master.number
            
            cond = master.getConditionDict()
            if cond:
                arr = conditions[master.eventid] = conditions.get(master.eventid) or []
                arr.extend(cond.keys())
            
            arr = exists[master.eventid] = exists.get(master.eventid) or []
            arr.append(master.number)
        
        for eventid, arr in conditions.items():
            ev_exists = exists.get(eventid)
            if not (ev_exists and len(list(set(arr) - set(ev_exists))) == 0):
                errors.append(u'不正な特別条件:eventid=%d, number=%s' % (eventid, list(set(arr) - set(ev_exists))))
        
        if errors:
            raise ModelEditValidError('<br />'.join(errors))

def main(request):
    return Handler.run(request)
