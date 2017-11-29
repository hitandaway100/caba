# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.kpi.base import KpiHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster
from platinumegg.app.cabaret.views.mgr.model_edit import AppModelChoiceField
import os
from django import forms


class Handler(KpiHandler):
    """バトルイベント参加率.
    """
    
    class Form(forms.Form):
        eventid = AppModelChoiceField(BattleEventMaster, required=False, label=u'イベントID')
    
    def getTitle(self):
        return u'バトルイベント日別参加数'
    
    def getKpiName(self):
        eventid = self.request.get("eventid")
        if not eventid or not str(eventid).isdigit():
            config = BackendApi.get_current_battleeventconfig(self.getModelMgr(), using=settings.DB_READONLY)
            eventid = config.mid
        self.__eventid = eventid
        return 'battleeventjoindaily_%03d' % int(eventid)
    
    def getOptionalForm(self):
        form = Handler.Form()
        form.eventid = self.__eventid
        return form
    
    def makeFileDataTable(self, dirpath, filelist):
        tabledata = []
        for filedata in filelist:
            filepath = os.path.join(dirpath, filedata['filename'])
            f = None
            data = None
            try:
                f = open(filepath)
                data = f.read()
                f.close()
            except:
                if f:
                    f.close()
                raise
            tabledata.append(data.split(','))
        return tabledata

def main(request):
    return Handler.run(request)
