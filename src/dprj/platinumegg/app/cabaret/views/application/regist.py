# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerRegist, PlayerTutorial, PlayerDXPWallConversion
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.dxp import DXPAPI
import settings_sub
import settings_sub_props
import settings
from enviroment_type import EnvironmentType
from platinumegg.app.cabaret.util.card import CardSet
import random
from platinumegg.lib.opensocial.util import OSAUtil

class Handler(AppHandler):
    """ユーザ登録ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRegist, PlayerTutorial]
    
    def process(self):
        viewer_id = self.osa_util.viewer_id
        uid = BackendApi.dmmid_to_appuid(self, [viewer_id]).get(viewer_id, None)
        if uid is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError('User not found. viewer_id=%s' % viewer_id)
            self.redirectToTop()
            return
        self.__uid = uid
        
        self.__args = self.getUrlArgs('/regist/')
        proc = self.__args.get(0)
        
        table = {
            'op' : self.procOpening,
            'yesno' : self.procYesno,
            'write' : self.procWrite,
            'decide' : self.procDecide,
        }
        func = table.get(proc, self.procSelect)
        func()

    def setTutorialHead(self, state):
        self.html_param['is_tutorial'] = True
        self.html_param['tutorial_title'] = Defines.TutorialStatus.NAMES[state]
        self.html_param['tutorial_page'] = Defines.TutorialStatus.FLOW_EXCLUDE_ANIMATIONS.index(state) + 1
        self.html_param['tutorial_page_max'] = len(Defines.TutorialStatus.FLOW_EXCLUDE_ANIMATIONS)
    
    def procOpening(self):
        """オープニング.
        """
        v_player = self.__getViewerPlayer()
        if v_player is None:
            return
        
        effectpath = 'op/effect.html'
        
        ptype = random.choice(Defines.CharacterType.LIST)
        params = {
            'backUrl':self.makeAppLinkUrl(UrlMaker.regist_yesno(ptype)),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def procSelect(self):
        """タイプ選択画面.
        """
        v_player = self.__getViewerPlayer()
        if v_player is None:
            return
        
        model_mgr = self.getModelMgr()
        leaders = BackendApi.get_defaultleaders(model_mgr, Defines.CharacterType.NAMES.keys(), using=settings.DB_READONLY)
        
        obj_leaders = {}
        urls = {}
        
        for k in Defines.CharacterType.NAMES.keys():
            if leaders.has_key(k):
                obj_leaders[k] = Objects.cardmaster(self, leaders[k])
            urls[k] = self.makeAppLinkUrl(UrlMaker.regist_yesno(k, first=False))
        
        self.html_param['url_enters'] = urls
        self.html_param['leaders'] = obj_leaders
        
        self.setTutorialHead(Defines.TutorialStatus.REGIST_SELECT)
        
        self.writeAppHtml('regist/select')
    
    def procYesno(self):
        """タイプ選択確認.
        """
        v_player = self.__getViewerPlayer()
        if v_player is None:
            return
        ptype = self.getSelectedType()
        if ptype is None:
            return
        
        model_mgr = self.getModelMgr()
        leader = BackendApi.get_defaultleaders(model_mgr, Defines.CharacterType.NAMES.keys(), using=settings.DB_READONLY).get(ptype)
        if leader:
            cardset = CardSet(BackendApi.create_card_by_master(leader), leader)
            self.html_param['leader'] = Objects.card(self, cardset)
        self.html_param['ptype'] = ptype
        self.html_param['is_first'] = self.__args.get(2) == '1'
        self.html_param['url_write'] = self.makeAppLinkUrl(UrlMaker.regist_write(ptype))
        self.html_param['url_back'] = self.makeAppLinkUrl(UrlMaker.regist_select())
        
        self.setTutorialHead(Defines.TutorialStatus.REGIST_SELECT)
        
        self.writeAppHtml('regist/yesno')
    
    def procWrite(self):
        """タイプ選択書き込み.
        """
        v_player = self.__getViewerPlayer()
        if v_player is None:
            return
        ptype = self.getSelectedType()
        if ptype is None:
            return

        try:
            if self.is_active_dxp():
                is_set_conversion = self.get_is_set_conversion()
            else:
                is_set_conversion = False
            model_mgr = db_util.run_in_transaction(self.tr_write_regist, v_player.id, ptype, is_set_conversion)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'登録済みです')
            else:
                raise
        
        if self.is_pc:
            #self.writeAppJson()
            url = UrlMaker.regist_decide()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
        else:
            url = UrlMaker.regist_decide()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))

    def get_is_set_conversion(self):
        if settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.RELEASE:
            is_rel = True
        else:
            is_rel = False
        dxpapi = DXPAPI(is_rel=is_rel)
        conversion_id = self.get_conversion_id(dxpapi, self.osa_util.viewer_id)
        is_conversion_regist_result = False
        if conversion_id and dxpapi.set_wall_conversion(conversion_id=conversion_id):
            is_conversion_regist_result = True
        return is_conversion_regist_result

    def get_conversion_id(self, dxpapi, viewer_id):
        conversion_id = dxpapi.get_wall_conversion(self.app_id,viewer_id)
        return conversion_id

    def procDecide(self):
        """タイプ選択完了.
        """
        v_player = self.getViewerPlayer()
        if v_player.tutorialstate != Defines.TutorialStatus.REGIST_COMPLETE:
            self.redirectToTop()
            return
        ptype = v_player.ptype
        
        model_mgr = self.getModelMgr()
        leader = BackendApi.get_defaultleaders(model_mgr, Defines.CharacterType.NAMES.keys(), using=settings.DB_READONLY).get(ptype)
        if leader:
            cardset = CardSet(BackendApi.create_card_by_master(leader), leader)
            self.html_param['leader'] = Objects.card(self, cardset)
        self.html_param['ptype'] = ptype
        self.html_param['url_enter'] = self.makeAppLinkUrl(UrlMaker.tutorial())
        
        self.setTutorialHead(Defines.TutorialStatus.REGIST_COMPLETE)
        
        self.writeAppHtml('regist/decide')
    
    def __getViewerPlayer(self):
        v_player = self.getViewerPlayer(quiet=True)
        playerTutorial = v_player.getModel(PlayerTutorial)
        if playerTutorial:
            # 登録済み.
            if playerTutorial.tutorialstate == Defines.TutorialStatus.REGIST_COMPLETE:
                url = UrlMaker.regist_decide()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
            else:
                self.redirectToTop()
            return None
        return v_player
    
    def getSelectedType(self):
        if self.is_pc:
            #ptype = self.request.get(Defines.URLQUERY_CTYPE, '')
            ptype = self.__args.get(1) or ""
        else:
            ptype = self.__args.get(1) or ""
        if not ptype or not ptype.isdigit() or not int(ptype) in Defines.CharacterType.NAMES.keys():
            self.redirectToTop()
            return None
        return int(ptype)
    
    def tr_write_regist(self, uid, ptype, is_set_conversion):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_regist_player(model_mgr, uid, ptype)

        player_dxp = PlayerDXPWallConversion.makeInstance(uid)
        player_dxp.is_set_conversion = is_set_conversion
        model_mgr.set_save(player_dxp)

        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
