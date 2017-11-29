# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.promotion import PromotionUtil


class Handler(AppHandler):
    """外部向けクロスプロモーションデバッグページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp]
    
    def process(self):
        
        args = self.getUrlArgs('/promotiondebug/')
        appname = args.get(0, '')
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        config = BackendApi.get_promotionconfig(model_mgr, appname, using=settings.DB_READONLY, do_get_closed=True)
        if config is None:
            raise CabaretError(u'未登録のアプリです:%s' % appname, CabaretError.Code.ILLEGAL_ARGS)
        
        function_name = self.request.get('_proc')
        if function_name:
            func = getattr(self, 'proc_%s' % function_name)
            if func:
                func(appname)
                if self.response.isEnd:
                    return
        
        requirementlist = BackendApi.get_promotionrequirementmaster_all(model_mgr, appname, using=settings.DB_READONLY)
        requirementlist.sort(key=lambda x:x.id)
        self.html_param['requirementlist'] = [{'text' : requirement.text, 'flag' : BackendApi.check_promotionrequirement(self, v_player.id, requirement)} for requirement in requirementlist]
        
        prizelist = BackendApi.get_promotionprizemaster_all(model_mgr, appname, using=settings.DB_READONLY)
        prizelist.sort(key=lambda x:((x.rid << 32) + x.id))
        userdata_dict = BackendApi.get_promotion_userdata(model_mgr, appname, v_player.id, [prize.id for prize in prizelist], using=settings.DB_READONLY)
        obj_prizelist = []
        for prize in prizelist:
            userdata = userdata_dict.get(prize.id)
            obj_prizelist.append({
                'id' : prize.id,
                'name' : prize.name,
                'status' : userdata.status if userdata else Defines.PromotionStatus.NONE,
            })
        self.html_param['prizelist'] = obj_prizelist
        
        self.html_param['level'] = v_player.level
        
        self.html_param['url_self'] = self.makeAppLinkUrl('/promotiondebug/%s/' % appname)
        
        self.html_param['url_promotion_top'] = self.makeAppLinkUrl(UrlMaker.promotion_top(appname))
        
        self.writeAppHtml('promotion/%s/debug' % config.htmlname)
    
    def proc_update_requirement(self, appname):
        """達成状態を変更.
        """
        level = self.request.get('level')
        if not level.isdigit():
            self.__setResultInfo(u'レベルは1以上の数値で入力してください', True)
            return
        
        model_mgr = self.getModelMgr()
        maxlevel = BackendApi.get_playermaxlevel(model_mgr, using=settings.DB_READONLY)
        level = max(0, min(maxlevel, int(level)))
        
        v_player = self.getViewerPlayer()
        
        def tr(uid, level):
            model_mgr = ModelRequestMgr()
            player = BackendApi.get_player(self, uid, [PlayerExp], model_mgr=model_mgr)
            playerexp = BackendApi.get_playerlevelexp_bylevel(level, model_mgr)
            if playerexp is None:
                playerexp = BackendApi.get_playerlevelexp_bylevel(maxlevel, model_mgr)
            player.exp = 0
            BackendApi.tr_add_exp(model_mgr, player, playerexp.exp)
            model_mgr.write_all()
            return model_mgr, player.getModel(PlayerExp)
        model_mgr, playerexp = db_util.run_in_transaction(tr, v_player.id, level)
        model_mgr.write_end()
        
        v_player.setModel(playerexp)
        self.__setResultInfo(u'プレイヤーレベルを%dに変更しました' % level)
    
    def proc_update_prizedata(self, appname):
        """報酬受取ステータスを変更.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        prizelist = BackendApi.get_promotionrequirementmaster_all(model_mgr, appname, using=settings.DB_READONLY)
        status_table = {}
        for prize in prizelist:
            status = self.request.get('prize_%s' % prize.id)
            if not status or not status.isdigit():
                status = Defines.PromotionStatus.NONE
            else:
                status = int(status)
                if not Defines.PromotionStatus.NAMES.has_key(status):
                    status = Defines.PromotionStatus.NONE
            status_table[prize.id] = status
        
        model_cls = PromotionUtil.getPromotionDataCls(appname)
        
        def tr(model_cls, uid, status_table):
            model_mgr = ModelRequestMgr()
            for k,v in status_table.items():
                key = model_cls.makeID(uid, k)
                model = model_mgr.get_model(model_cls, key, get_instance=True)
                if model.status != v:
                    model.status = v
                    if model.status == Defines.PromotionStatus.RECEIVED:
                        model.rtime = OSAUtil.get_now()
                    model_mgr.set_save(model)
            model_mgr.write_all()
            return model_mgr
        db_util.run_in_transaction(tr, model_cls, v_player.id, status_table).write_end()
        
        self.__setResultInfo(u'報酬受取り状態を変更しました')
    
    def __setResultInfo(self, msg, is_error=False):
        self.html_param['result_info'] = {
            'msg' : msg,
            'is_error' : is_error,
        }
    

def main(request):
    return Handler.run(request)
