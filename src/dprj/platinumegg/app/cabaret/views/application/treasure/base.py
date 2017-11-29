# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
import settings
from platinumegg.lib.opensocial.util import OSAUtil

class TreasureHandler(AppHandler):
    """宝箱.
    """
    
    def putTreasureListParams(self, ttype, do_check_all=False, using=settings.DB_READONLY):
        
        target_obj = self.html_param
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # カード上限.
        overlimit = v_player.cardlimit <= BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        target_obj['overlimit'] = overlimit
        
        # 宝箱を開けられるか.
        openable = BackendApi.check_treasure_openable(model_mgr, v_player, ttype, using=settings.DB_READONLY)
        target_obj['is_openable'] = openable
        
        # 宝箱名前.
        target_obj['treasure_name'] = Defines.TreasureType.NAMES[ttype]
        
        # 宝箱の数.
        treasure_nums = {}
        for treasure_type in Defines.TreasureType.NAMES.keys():
            treasure_nums[treasure_type] = BackendApi.get_treasure_num(model_mgr, treasure_type, v_player.id, using=using)
        target_obj['treasure_nums'] = treasure_nums
        
        # 宝箱のデータ.
        treasurelist_dict = {}
        if do_check_all:
            ttype_list = Defines.TreasureType.NAMES.keys()
        else:
            ttype_list = [ttype]
        
        for tt in ttype_list:
            treasure_num = treasure_nums[tt]
            pool_limit = Defines.TreasureType.POOL_LIMIT[tt]
            if 0 < treasure_num:
                treasureidlist = BackendApi.get_treasure_idlist(model_mgr, tt, v_player.id, 0, treasure_num, using=using)
                treasurelist = BackendApi.get_treasure_list(model_mgr, tt, treasureidlist, using=using)
                if len(treasureidlist) != len(treasurelist):
                    # ずれてる.
                    treasure_num = len(BackendApi._save_treasureidlist(model_mgr, v_player.id, tt, using=using))
                    treasureidlist = BackendApi.get_treasure_idlist(model_mgr, tt, v_player.id, 0, treasure_num, using=using)
                    treasurelist = BackendApi.get_treasure_list(model_mgr, tt, treasureidlist, using=using)
                    treasure_nums[tt] = treasure_num
                treasurelist_dict[tt] = treasurelist[:pool_limit]
            treasure_nums[tt] = min(pool_limit, treasure_nums[tt])
        
        # 鍵情報.
        treasurekey = Objects.key(self, v_player)
        self.html_param['treasurekey'] = treasurekey
        keydata = treasurekey.get(Defines.TreasureType.STRING.get(ttype, 'unknown'))
        key_num = None
        if keydata:
            key_num = keydata['num']
        
        treasure_num = treasure_nums[ttype]
        treasurelist = treasurelist_dict.get(ttype) or []
        treasurelist.sort(key=lambda x:x.etime)
        obj_treasurelist = []
        str_treasureidlist = []
        for treasure in treasurelist:
            obj_treasurelist.append(Objects.treasure(self, treasure, ttype))
            str_treasureidlist.append('%d' % treasure.id)
        target_obj['treasurelist'] = obj_treasurelist
        if key_num is not None:
            str_treasureidlist = str_treasureidlist[:key_num]
        
        if str_treasureidlist:
            # 一括受け取りのURL.
            url = UrlMaker.treasureget(ttype)
            self.html_param['allopendata'] = {
                'url' : self.makeAppLinkUrl(url),
                'id' : str_treasureidlist,
            }
        
        # 宝箱の中身.
        masteridlist = BackendApi.get_public_treasuremaster_idlist(model_mgr, ttype, using=settings.DB_READONLY)
        masterlist = BackendApi.get_treasuremaster_list(model_mgr, ttype, masteridlist, using=settings.DB_READONLY)
        target_obj['treasure_item_list'] = BackendApi.make_treasureiteminfo_list(self, masterlist)
        
        # 選択している宝箱のタイプ.
        self.html_param['treasure_type'] = ttype
        self.html_param['str_treasure_type'] = Defines.TreasureType.STRING.get(ttype, None)
        
        def makeURL(tt):
            url = UrlMaker.treasurelist(tt)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_FLAG, 1)
            return self.makeAppLinkUrl(url)
        
        # 遷移先URL.
        self.html_param['url_treasure_gold'] = makeURL(Defines.TreasureType.GOLD)
        self.html_param['url_treasure_silver'] = makeURL(Defines.TreasureType.SILVER)
        self.html_param['url_treasure_bronze'] = makeURL(Defines.TreasureType.BRONZE)
