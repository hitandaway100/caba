# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Shop import ShopItemBuyData
from defines import Defines


class ShopHandler(AppHandler):
    """ショップのハンドラ.
    """
    
    def preprocess(self):
        AppHandler.preprocess(self)
        self.__shopmaster_id = None
        self.__shopmaster = None
        self.__buydata = None
    
    def set_masterid(self, mid):
        self.__shopmaster_id = mid
        self.__shopmaster = None
        self.__buydata = None
    
    def getShopMaster(self):
        """マスターデータ.
        """
        if self.__shopmaster is None:
            model_mgr = self.getModelMgr()
            self.__shopmaster = BackendApi.get_shopmaster(model_mgr, self.__shopmaster_id, using=settings.DB_READONLY)
            if self.__shopmaster is None:
                raise CabaretError(u'存在しない商品です', CabaretError.Code.INVALID_MASTERDATA)
        return self.__shopmaster
    
    def checkSchedule(self, master):
        """マスターデータのスケジュールを確認.
        """
        model_mgr = self.getModelMgr()
        BackendApi.check_schedule(model_mgr, master.schedule, using=settings.DB_READONLY)
    
    def getShopBuyData(self, blank=False):
        """購入情報.
        """
        if self.__buydata is None:
            v_player = self.getViewerPlayer()
            master = self.getShopMaster()
            model_mgr = self.getModelMgr()
            self.__buydata = BackendApi.get_shopbuydata(model_mgr, v_player.id, [master.id], using=settings.DB_READONLY).get(master.id)
            if self.__buydata is None and not blank:
                # 明らかに不正アクセス.
                raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        return self.__buydata
    
    def makeShopObj(self):
        """商品情報作成.
        """
        v_player = self.getViewerPlayer()
        
        master = self.getShopMaster()
        buydata = self.getShopBuyData(blank=master.consumetype!=Defines.ShopConsumeType.PAYMENT)
        
        return BackendApi.make_shopitem_obj(self, master, v_player, buydata)
    
    def putBuyableShopItemList(self):
        """購入可能な商品リスト.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        masterlist = BackendApi.get_buyable_shopitemlist(model_mgr, v_player, using=settings.DB_READONLY)
        buydatas = BackendApi.get_shopbuydata(model_mgr, v_player.id, [master.id for master in masterlist], using=settings.DB_READONLY)
        
        shopitemlist = []
        for master in masterlist:
            shopitemlist.append(BackendApi.make_shopitem_obj(self, master, v_player, buydatas.get(master.id)))
        
        self.html_param['shopitemlist'] = shopitemlist
    
    @staticmethod
    def tr_write_buydata(uid, mid):
        """購入情報がないので用意.
        """
        model_mgr = ModelRequestMgr()
        ins = ShopItemBuyData.makeInstance(ShopItemBuyData.makeID(uid, mid))
        model_mgr.set_save(ins)
        model_mgr.write_all()
        return model_mgr
