# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.promotion import PromotionUtil


class Handler(AppHandler):
    """クロスプロモーションTOPページ.
    """
    
    def process(self):
        args = self.getUrlArgs('/promotionprize/')
        appname = args.get(1)
        self.__appname = appname
        
        model_mgr = self.getModelMgr()
        config = BackendApi.get_promotionconfig(model_mgr, appname, using=settings.DB_READONLY)
        if config is None:
            # アプリが存在しない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        proc = args.get(0)
        table = {
            'list' : self.procList,
            'receiveyesno' : self.procYesno,
            'receivedo' : self.procDo,
            'receivecomplete' : self.procComplete,
        }
        
        self.html_param['url_promotion_top'] = self.makeAppLinkUrl(UrlMaker.promotion_top(self.__appname))
        self.html_param['url_promotion_prizelist'] = self.makeAppLinkUrl(UrlMaker.promotion_prizelist(self.__appname))
        
        self.html_param['url_promotion_app'] = PromotionUtil.chooseApplicationUrl(self, config)
        
        table.get(proc, self.procList)(args, config)
    
    def procList(self, args, config):
        """報酬受取.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 報酬一覧取得.
        prizemaster_all = BackendApi.get_promotionprizemaster_all(model_mgr, self.__appname, using=settings.DB_READONLY)
        requirement_idlist = list(set([prizemaster.rid for prizemaster in prizemaster_all]))
        
        # 達成条件問い合わせ.
        requirement_texts = self.getRequirementText(requirement_idlist)
        requirement_idlist = [int(str(k)) for k in requirement_texts.keys() if str(k).isdigit()]
        prizemaster_dict = dict([(prizemaster.id, prizemaster) for prizemaster in prizemaster_all if prizemaster.rid in requirement_idlist])
        
        # 達成状況確認.
        userdata_dict = BackendApi.get_promotion_userdata(model_mgr, self.__appname, uid, prizemaster_dict.keys(), using=settings.DB_READONLY)
        call_target_requirement_table = {}
        for prizemaster in prizemaster_dict.values():
            userdata = userdata_dict.get(prizemaster.id)
            if userdata is None or userdata.status == Defines.PromotionStatus.NONE:
                call_target_requirement_table[prizemaster.id] = prizemaster.rid
        
        # 達成状況問い合わせ.
        flags = self.getRequirementStatus(list(set(call_target_requirement_table.values())))
        
        # 達成状況更新.
        if flags:
            achieved_midlist = [mid for mid, rid in call_target_requirement_table.items() if flags.get(str(rid))]
            if achieved_midlist:
                wrote_model_mgr, wrote_userdata_dict = db_util.run_in_transaction(Handler.tr_write_achieve, self.__appname, uid, achieved_midlist)
                wrote_model_mgr.write_end()
                userdata_dict.update(wrote_userdata_dict)
        
        # 報酬情報一覧作成.
        prizemaster_list = prizemaster_dict.values()[:]
        prizemaster_list.sort(key=lambda x:((x.rid << 32)+x.id))
        self.html_param['promotioninfo'] = BackendApi.make_promotion_prizeinfo(self, self.__appname, prizemaster_list, requirement_texts, userdata_dict)
        
        # TOPページ.
        self.html_param['url_promotion_top'] = self.makeAppLinkUrl(UrlMaker.promotion_top(self.__appname))
        
        self.writeAppHtml('promotion/%s/prizelist' % config.htmlname)
    
    def procYesno(self, args, config):
        """受け取り確認.
        """
        mid = args.getInt(2)
        master = self.getPromotionPrizeMaster(mid)
        if master is None:
            return
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        requirement_id = master.rid
        
        # 達成条件問い合わせ.
        requirement_text = self.getRequirementText([requirement_id]).get(str(requirement_id))
        if not requirement_text:
            # 非公開.
            url = UrlMaker.promotion_prizelist(self.__appname)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 達成確認.
        userdata = BackendApi.get_promotion_userdata(model_mgr, self.__appname, uid, [mid], using=settings.DB_READONLY).get(mid)
        if userdata is None or userdata.status == Defines.PromotionStatus.NONE:
            # 達成状況問い合わせ.
            flags = self.getRequirementStatus([mid])
            if flags.get(str(mid)):
                wrote_model_mgr, wrote_userdata_dict = db_util.run_in_transaction(Handler.tr_write_achieve, self.__appname, uid, [mid])
                wrote_model_mgr.write_end()
                userdata = wrote_userdata_dict.get(mid) or userdata
        
        obj_promotioninfo_data = None
        obj_promotioninfo = BackendApi.make_promotion_prizeinfo(self, self.__appname, [master], {mid:requirement_text}, {mid:userdata})
        if obj_promotioninfo:
            if obj_promotioninfo['list']:
                obj_promotioninfo_data = obj_promotioninfo['list'][0]
        
        if obj_promotioninfo_data is None:
            # 非対応.
            url = UrlMaker.promotion_prizelist(self.__appname)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.html_param['promotioninfo_data'] = obj_promotioninfo_data
        
        # 受け取りリンク.
        self.html_param['url_promotion_do'] = self.makeAppLinkUrl(UrlMaker.promotion_prizereceive_do(self.__appname, mid))
        
        self.writeAppHtml('promotion/%s/yesno' % config.htmlname)
    
    def procDo(self, args, config):
        """受け取り書き込み.
        """
        mid = args.getInt(2)
        master = self.getPromotionPrizeMaster(mid)
        if master is None:
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        url = UrlMaker.promotion_prizereceive_complete(self.__appname, mid)
        try:
            db_util.run_in_transaction(Handler.tr_write_receive, self.__appname, uid, master).write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                url = UrlMaker.promotion_prizereceive_yesno(self.__appname, mid)
        
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procComplete(self, args, config):
        """受け取り完了.
        """
        mid = args.getInt(2)
        master = self.getPromotionPrizeMaster(mid)
        if master is None:
            return
        
        obj_promotioninfo_data = None
        obj_promotioninfo = BackendApi.make_promotion_prizeinfo(self, self.__appname, [master], {mid:u'未取得'}, {})
        if obj_promotioninfo:
            if obj_promotioninfo['list']:
                obj_promotioninfo_data = obj_promotioninfo['list'][0]
        
        if obj_promotioninfo_data is None:
            # 非対応.
            url = UrlMaker.promotion_prizelist(self.__appname)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.html_param['promotioninfo_data'] = obj_promotioninfo_data
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 報酬一覧取得.
        prizemaster_all = BackendApi.get_promotionprizemaster_all(model_mgr, self.__appname, using=settings.DB_READONLY)
        requirement_idlist = list(set([prizemaster.rid for prizemaster in prizemaster_all]))
        
        # 達成条件問い合わせ.
        requirement_texts = self.getRequirementText(requirement_idlist)
        requirement_idlist = [int(str(k)) for k in requirement_texts.keys() if str(k).isdigit()]
        prizemaster_dict = dict([(prizemaster.id, prizemaster) for prizemaster in prizemaster_all if prizemaster.rid in requirement_idlist])
        
        # 達成状況確認.
        userdata_dict = BackendApi.get_promotion_userdata(model_mgr, self.__appname, uid, prizemaster_dict.keys(), using=settings.DB_READONLY)
        is_allend = True
        for prizemaster_id in prizemaster_dict.keys():
            userdata = userdata_dict.get(prizemaster_id)
            if userdata is None or userdata.status != Defines.PromotionStatus.RECEIVED:
                is_allend = False
                break
        self.html_param['is_allend'] = is_allend
        
        self.writeAppHtml('promotion/%s/complete' % config.htmlname)
    
    def getRequirementText(self, requirement_idlist, do_execute=True):
        """達成条件テキストを取得.
        """
        try:
            return PromotionUtil.requestPromotionConditionGet(self, self.__appname, requirement_idlist, do_execute=do_execute)
        except CabaretError, err:
            self.addlogerror(err.value)
            return {}
    
    def getRequirementStatus(self, requirement_idlist, do_execute=True):
        """達成状況を問い合わせ.
        """
        if not requirement_idlist:
            return {}
        
        v_player = self.getViewerPlayer()
        try:
            return PromotionUtil.requestPromotionAchieveFlags(self, self.__appname, v_player.dmmid, requirement_idlist, do_execute=do_execute)
        except CabaretError, err:
            self.addlogerror(err.value)
            return {}
    
    def getPromotionPrizeMaster(self, mid):
        model_mgr = self.getModelMgr()
        
        master = None
        if mid:
            master = BackendApi.get_promotionprizemaster(model_mgr, self.__appname, mid, using=settings.DB_READONLY)
        
        if master is None:
            url = UrlMaker.promotion_prizelist(self.__appname)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
        
        return master
    
    @staticmethod
    def tr_write_achieve(appname, uid, midlist):
        model_mgr = ModelRequestMgr()
        userdata_dict = BackendApi.tr_achieve_promotion(model_mgr, appname, uid, midlist)
        model_mgr.write_all()
        return model_mgr, userdata_dict
    
    @staticmethod
    def tr_write_receive(appname, uid, master):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_receive_promotionprize(model_mgr, appname, uid, master)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
