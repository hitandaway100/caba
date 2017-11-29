# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaPlayData
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.util.gacha import GachaBox, GachaBoxGroup
from platinumegg.app.cabaret.util.apprandom import AppRandom
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """ガチャのシミュレータ.
    """
    
    def process(self):
        
        if self.request.method == "POST":
            self.procPost()
        
        model_mgr = self.getModelMgr()
        
        self.html_param['gachamaster_list'] = model_mgr.get_mastermodel_all(GachaMaster, order_by='-id', using=backup_db)
        
        self.writeAppHtml('/simulator/gacha_simulator')
    
    def procPost(self):
        """パラメータを受け取ってガチャ情報を用意する.
        """
        model_mgr = self.getModelMgr()
        
        # ガチャのマスターID.
        strmid = str(self.request.get('_mid') or self.request.get('_strmid')) or 0
        gachamaster = None
        if strmid.isdigit():
            mid = int(strmid)
            gachamaster = BackendApi.get_gachamaster(model_mgr, mid, using=backup_db)
        
        if gachamaster is None:
            self.putAlertToHtmlParam(u'存在しないガチャです.%s' % strmid, AlertCode.ERROR)
            return
        
        self.html_param['cur_gachamaster'] = gachamaster
        
        # 試験回数.
        strcnt = str(self.request.get('_cnt') or 0)
        cnt = 0
        if strcnt.isdigit():
            cnt = int(strcnt)
        if cnt < 1:
            self.putAlertToHtmlParam(u'試験回数は自然数で指定してください.', AlertCode.ERROR)
            return
        
        cnt = min(1000000, cnt)
        self.html_param['cnt'] = cnt
        
        # 試験.
        self.__testGacha(gachamaster, cnt)
    
    def __testGacha(self, gachamaster, cnt):
        """ガチャをテスト実行.
        """
        model_mgr = self.getModelMgr()
        
        test_playdata = GachaPlayData.makeInstance(GachaPlayData.makeID(0, gachamaster.boxid))
        
        # BOX.
        box = GachaBox(gachamaster, test_playdata)
        groupidlist = box.get_group_id_list()
        groupdict = dict([(groupmaster.id, GachaBoxGroup(groupmaster)) for groupmaster in BackendApi.get_gachagroupmaster_list(model_mgr, groupidlist, using=backup_db)])
        
        # 設定値.
        group_rate_dict = {}
        cardrate_dict = {}
        cardgroup_dict = {}
        for groupid in groupidlist:
            rate = box.get_group_rate(groupid)
            group_rate_dict[groupid] = group_rate_dict.get(groupid, 0) + rate
            
            group_cardrate_dict = {}
            group = groupdict[groupid]
            for carddata in group.carddata_list:
                cardid = carddata.card
                group_cardrate_dict[cardid] = group_cardrate_dict.get(cardid, 0) + carddata.rate
                
                arr = cardgroup_dict[cardid] = cardgroup_dict.get(cardid) or []
                arr.append(groupid)
            
            cardrate_dict[groupid] = group_cardrate_dict
        
        # ランダム.
        rand = AppRandom()
        
#        result_list = []
        distribution_dict = dict.fromkeys(cardgroup_dict.keys(), 0)
        group_distribution_dict = dict.fromkeys(groupdict.keys(), 0)
        
        def addResult(cardid, point, groupid):
#            result_list.append((cardid, point, groupid))
            distribution_dict[cardid] = (distribution_dict.get(cardid) or 0) + 1
            group_distribution_dict[groupid] = (group_distribution_dict.get(groupid) or 0) + 1
        
        # ランキングガチャ用ポイント獲得関数.
        point_getter = lambda x : 0
        if gachamaster.consumetype == Defines.GachaConsumeType.RANKING:
            rankinggachamaster = BackendApi.get_rankinggacha_master(model_mgr, gachamaster.boxid, using=backup_db)
            if rankinggachamaster:
                randmax = rankinggachamaster.randmax
                randmin = rankinggachamaster.randmin
                point_getter = lambda x : x.point * (100+rand.getIntN(randmin+randmax)-randmin) / 100
        
        # BOXからグループを選択.
        groupidlist = []
        for _ in xrange(cnt):
            if box.is_empty:
                # 空になったのでリセット.
                test_playdata.resetGroupCounts()
                box = GachaBox(gachamaster, test_playdata)
            groupid, _ = box.select(rand)
            group = groupdict[groupid]
            carddata = group.select_obj(rand)
            addResult(carddata.card, point_getter(carddata), groupid)
        
#        self.html_param['result_list'] = result_list
        self.html_param['distribution_dict'] = distribution_dict
        self.html_param['group_dict'] = groupdict
        self.html_param['group_distribution_dict'] = group_distribution_dict
        self.html_param['group_rate_dict'] = group_rate_dict
        self.html_param['group_rate_total'] = sum(group_rate_dict.values())
        self.html_param['cardrate_dict'] = cardrate_dict
        self.html_param['cardgroup_dict'] = cardgroup_dict
        
        cardmaster_idlist = distribution_dict.keys()
        cardmaster_dict = BackendApi.get_cardmasters(cardmaster_idlist, model_mgr, using=backup_db)
        self.html_param['cardmaster_dict'] = cardmaster_dict
    
def main(request):
    return Handler.run(request)
