# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.panelmission.base import PanelMissionHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerDataWeekly
from defines import Defines

class Handler(PanelMissionHandler):
    """パネルミッションTopページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [
            PlayerExp,
        ]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        using = settings.DB_READONLY
        now = OSAUtil.get_now()
        
        # 現在のパネル.
        is_cleared = False
        panelmission_player = BackendApi.get_panelmission_player(model_mgr, uid, using=using)
        cur_panelmaster = BackendApi.get_panelmission_panelmaster(model_mgr, panelmission_player.panel, using=using)
        if cur_panelmaster is None:
            cur_panelmaster = BackendApi.get_panelmission_panelmaster(model_mgr, panelmission_player.panel - 1, using=using)
            if cur_panelmaster is None:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'パネルが存在しません')
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
                return
            is_cleared = True
        panelid = cur_panelmaster.id
        
        # このパネルのミッション.
        mission_list = BackendApi.get_panelmission_missionmaster_by_panelid(model_mgr, panelid, using=using)
        
        # 進行状況.
        missionplaydata = None
        if not is_cleared:
            missionplaydata = BackendApi.get_panelmission_data(model_mgr, uid, panelid, using=using, for_update=False)
            # 名誉ポイントの確認とフラグの調整.
            caba_score = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_DEFAULT)
            if caba_score:
                for i, mission in enumerate(mission_list, 1):
                    if mission.condition_type == Defines.PanelMissionCondition.HONOR_POINT:
                        if mission.condition_value1 <= caba_score.point:
                            setattr(missionplaydata, 'etime{}'.format(i), now)
            # 売上と集客数の確認とフラグの調整.
            caba_data = BackendApi.get_cabaretclub_scoreplayerdata_weekly(model_mgr, uid, now, using=settings.DB_READONLY)
            if caba_data:
                for i, mission in enumerate(mission_list, 1):
                    if mission.condition_type == Defines.PanelMissionCondition.PROCEEDS:
                        if mission.condition_value1 * 1000 <= caba_data.proceeds:
                            setattr(missionplaydata, 'etime{}'.format(i), now)
                    elif mission.condition_type == Defines.PanelMissionCondition.CUSTOMER_TOTAL:
                        if mission.condition_value1 <= caba_data.customer:
                            setattr(missionplaydata, 'etime{}'.format(i), now)

        # ミッション情報.
        obj_mission_list = [BackendApi.make_panelmission_mission_htmlobj(self, v_player, missionmaster, is_cleared, missionplaydata, now, using=using) for missionmaster in mission_list]
        
        # パネル情報.
        obj_panel = BackendApi.make_panelmission_panel_htmlobj(self, cur_panelmaster, obj_mission_list, is_cleared, using=using)
        self.html_param['panelmission'] = obj_panel
        
        # HTML出力.
        self.writeAppHtml('panelmission')

def main(request):
    return Handler.run(request)

