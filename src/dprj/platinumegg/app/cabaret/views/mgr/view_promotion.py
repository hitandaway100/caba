# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines
from platinumegg.lib.platform.api.objects import People, PeopleRequestData
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.app.cabaret.util.promotion import PromotionSettings,\
    PromotionUtil
from platinumegg.app.cabaret.models.Player import Player, PlayerCrossPromotion


class Handler(AdminHandler):
    """クロスプロモーション状態確認.
    """
    
    def process(self):
        
        args = self.getUrlArgs('/infomations/view_promotion/')
        dmmid = args.get(0) or ''
        
        model_mgr = self.getModelMgr()
        
        data = PeopleRequestData.createForPeople(dmmid)
        request = self.osa_util.makeApiRequest(ApiNames.People, data)
        reqkey = 'Person:%s' % dmmid
        self.addAppApiRequest(reqkey, request)
        
        ret_data = self.execute_api()
        try:
            person = ret_data[reqkey].get()
            if type(person) in (list, tuple):
                person = person[0]
        except:
            person = People.makeNotFound(dmmid)
        self.html_param['nickname'] = person.nickname
        
        appname = self.request.get('appname', PromotionSettings.Apps.KOIHIME)
        self.html_param['promotion_appname'] = appname
        self.html_param['promotion_apps'] = PromotionSettings.CONFIG.keys()
        
        # ギャングオブヘブンのプロモは別形式なので分ける
        if appname == 'Standard':
            uid = Player.getValues(filters={'dmmid': str(dmmid)}).id
            crosspromo_data = model_mgr.get_model(PlayerCrossPromotion, uid, using=settings.DB_READONLY)
            if crosspromo_data is None:
                self.html_param['displaylist'] = []
            else:
                self.html_param['displaylist'] = [
                    dmmid,
                    crosspromo_data.total_login_count,
                    crosspromo_data.is_battle,
                    crosspromo_data.is_battle_win_continue,
                    crosspromo_data.is_battle_rank5,
                    crosspromo_data.is_level10,
                    crosspromo_data.is_level20,
                    crosspromo_data.is_open_cabaclub,
                    crosspromo_data.is_trade_treasure,
                    crosspromo_data.is_acquired_ssr_card,
                ]
            self.writeAppHtml('infomations/view_promotion_standard')
            return

        master_cls = PromotionUtil.getPromotionPrizeMasterCls(appname)
        promotionmaster_all = model_mgr.get_mastermodel_all(master_cls, order_by='id', using=settings.DB_READONLY)
        midlist = [promotionmaster.id for promotionmaster in promotionmaster_all]
        
        uid = BackendApi.dmmid_to_appuid(self, [dmmid], using=settings.DB_READONLY).get(dmmid)
        if uid:
            userdata_dict = BackendApi.get_promotion_userdata(model_mgr, appname, uid, midlist, using=settings.DB_READONLY)
        else:
            userdata_dict = {}
        
        obj_prizelist = []
        for promotionmaster in promotionmaster_all:
            userdata = userdata_dict.get(promotionmaster.id)
            status = userdata.status if userdata else Defines.PromotionStatus.NONE
            atime = userdata.atime.strftime("%Y-%m-%d %H:%M:%S") if status != Defines.PromotionStatus.NONE else u'------'
            rtime = userdata.rtime.strftime("%Y-%m-%d %H:%M:%S") if status == Defines.PromotionStatus.RECEIVED else u'------'
            
            obj_prizelist.append({
                'id' : promotionmaster.id,
                'name' : promotionmaster.name,
                'status' : status,
                'str_status' : Defines.PromotionStatus.NAMES[status],
                'atime' : atime,
                'rtime' : rtime,
            })
        self.html_param['promotionprizelist'] = obj_prizelist
        
        self.writeAppHtml('infomations/view_promotion')
    

def main(request):
    return Handler.run(request)
