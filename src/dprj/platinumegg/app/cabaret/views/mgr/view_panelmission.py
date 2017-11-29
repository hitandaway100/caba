# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.models.Mission import PlayerPanelMission,\
    PanelMissionData
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.mission import PanelMissionConditionExecuter
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """パネルミッション状況.
    """
    def process(self):
        args = self.getUrlArgs('/infomations/view_panelmission/')
        uid = args.getInt(0)
        
        model_mgr = self.getModelMgr()
        
        self.html_param['now'] = OSAUtil.get_now()
        
        player = BackendApi.get_player(self, uid, [], using=backup_db, model_mgr=model_mgr)
        if player is None:
            self.putAlertToHtmlParam(u'存在しないプレイヤーです', alert_code=AlertCode.ERROR)
        else:
            person = BackendApi.get_dmmplayers(self, [player], using=backup_db).get(player.dmmid)
            self.html_param['player'] = Objects.player(self, player, person)
            
            # 現在のパネル.
            playerpanelmission = PlayerPanelMission.getByKey(uid, using=backup_db)
            cur_panelid = playerpanelmission.panel if playerpanelmission else 1
            
            # 進行情報.
            panelmissiondata_dict = dict([(model.mid, model) for model in PanelMissionData.fetchByOwner(uid, using=backup_db)])
            
            # 現在のパネルまでの進行情報.
            obj_panel_list = []
            for panelid in xrange(1, cur_panelid+1):
                panelmaster = BackendApi.get_panelmission_panelmaster(model_mgr, panelid, using=backup_db)
                if panelmaster is None:
                    continue
                
                missionmaster_list = BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, panelid, using=backup_db)
                panelmissiondata = panelmissiondata_dict.get(panelid)
                
                obj_mission_list = []
                is_cleared = cur_panelid < panelid
                for missionmaster in missionmaster_list:
                    obj_mission_list.append(self.__makeMissionObj(missionmaster, panelmissiondata, is_cleared))
                obj_panel_list.append({
                    'name' : panelmaster.name,
                    'current' : cur_panelid == panelid,
                    'missionlist' : obj_mission_list,
                    'stime' : panelmissiondata.stime if panelmissiondata else None
                })
            self.html_param['panellist'] = obj_panel_list[::-1]
        
        self.writeAppHtml('infomations/view_panelmission')
    
    def __makeMissionObj(self, missionmaster, panelmissiondata, is_cleared):
        """ミッション情報.
        """
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        uid = panelmissiondata.uid
        current_value = None
        missiondata = None
        
        target_value = PanelMissionConditionExecuter().getConditionValue(missionmaster)
        if panelmissiondata:
            missiondata = panelmissiondata.get_data(missionmaster.number)
            if is_cleared or missiondata['etime'] <= now:
                # 達成済み.
                current_value = target_value
            elif missionmaster.condition_type == Defines.PanelMissionCondition.BATTLE_RANK_UP:
                battleplayer = BackendApi.get_battleplayer(model_mgr, uid, using=settings.DB_READONLY)
                current_value = int(bool(battleplayer and missionmaster.condition_value1 <= battleplayer.rank))
            elif missionmaster.condition_type == Defines.PanelMissionCondition.AREA_COMPLETE:
                areaid = missionmaster.condition_value1
                areacomplete = BackendApi.get_areaplaydata(model_mgr, uid, [areaid], using=settings.DB_READONLY).get(areaid)
                current_value = int(areacomplete is not None)
            
            current_value = min(target_value, current_value if current_value is not None else missiondata['cnt'])
        else:
            current_value = target_value if is_cleared else 0
        
        return {
            'number' : missionmaster.number,
            'name' : missionmaster.name,
            'img_pre' : self.url_static + 'img/sp/large/' + missionmaster.image_pre,
            'img_post' : self.url_static + 'img/sp/large/' + missionmaster.image_post,
            'data' : missiondata or {},
            'cleared' : target_value <= current_value,
        }

def main(request):
    return Handler.run(request)
