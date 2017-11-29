# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.views.application.scout.base import ScoutHandler
from platinumegg.app.cabaret.models.Player import PlayerScout, PlayerAp,\
    PlayerGold, PlayerExp, PlayerDeck, PlayerFriend
import operator


class Handler(ScoutHandler):
    """スカウトTopページ.
    引数:
        プレイヤー情報.
        エリア情報.
        エリアのスカウト情報.
        スカウトのドロップアイテムの取得状況.
        ボス情報.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerScout, PlayerAp, PlayerGold, PlayerExp, PlayerDeck, PlayerFriend]
    
    def __putParam(self, key, value):
        if self.is_pc:
            #self.json_result_param[key] = value
            self.html_param[key] = value
        else:
            self.html_param[key] = value
    
    def process(self):
        
        try:
            # エリア.
            areaid = int(self.request.get(Defines.URLQUERY_AREA, 0)) or None
            #if self.is_pc and areaid is None:
            #    raise CabaretError()
        except:
            raise CabaretError(u'閲覧できないエリアです', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        # エリア.
        area = None
        if areaid:
            area = BackendApi.get_area(model_mgr, areaid, using)
        else:
            area = BackendApi.get_lastview_area(model_mgr, uid, using)
            if area is not None:
                areaid = area.id
        
        if area and not BackendApi.check_area_playable(model_mgr, area, uid, using):
            area = None
        
        if area is None:
            # 見つからなかったので最新のエリア.
            areaid = BackendApi.get_newbie_areaid(model_mgr, uid, using)
            area = BackendApi.get_area(model_mgr, areaid, using)
        
        # エリアクリア情報.
        areaplaydata = BackendApi.get_areaplaydata(model_mgr, uid, [area.id], using).get(area.id)
        self.__putParam('area', Objects.area(self, area, areaplaydata))
        
        # スカウト.
        scoutidlist = BackendApi.get_scoutidlist_by_area(model_mgr, area.id, using)
        scoutlist = BackendApi.get_scouts(model_mgr, scoutidlist, using)
        scoutlist.sort(key=operator.attrgetter('id'))
        
        # スカウト進行情報.
        pscoutidlist = scoutidlist[:]
        pscoutidlist.extend([scout.opencondition for scout in scoutlist if scout.opencondition])
        pscoutidlist = list(set(pscoutidlist))
        scoutplaydata_dict = BackendApi.get_scoutprogress(model_mgr, uid, pscoutidlist, using)
        
        obj_scoutlist = []
        allcleared = True
        for scout in scoutlist:
            if not BackendApi.check_scout_playable(model_mgr, scout, v_player, using):
                allcleared = False
                continue
            scoutplaydata = scoutplaydata_dict.get(scout.id)
            obj_scout = self.makeScoutObj(scout, scoutplaydata)
            obj_scoutlist.insert(0, obj_scout)
            if not obj_scout['cleared']:
                allcleared = False
        self.__putParam('scoutlist', obj_scoutlist)
        
        is_last_area = False
        if allcleared:
            if areaplaydata is None:
                # ボス出現.
                boss = BackendApi.get_boss(model_mgr, area.boss, using=using)
                if boss is None:
                    raise CabaretError(u'エリアにボスがいません.%d' % area.id, CabaretError.Code.INVALID_MASTERDATA)
                self.__putParam('boss', Objects.boss(self, boss))
                # ボス戦へのURL.
                url = UrlMaker.bosspre(areaid)
                self.html_param['url_bossbattle'] = self.makeAppLinkUrl(url)
            else:
                # クリア済み.
                next_area_id = BackendApi.get_next_areaid(model_mgr, area.id, using=settings.DB_READONLY)
                if next_area_id == area.id:
                    is_last_area = True
                else:
                    next_area = BackendApi.get_area(model_mgr, next_area_id, using=settings.DB_READONLY)
                    if not BackendApi.check_area_playable(model_mgr, next_area, uid, using=settings.DB_READONLY):
                        is_last_area = True
        self.html_param['is_last_area'] = is_last_area
        
        self.html_param['player'] = Objects.player(self, v_player, None)
        
        
        arealist = BackendApi.get_playable_area_all(model_mgr, uid, using=settings.DB_READONLY)
        prev_area = None
        post_area = None
        flag = False
        for tmparea in arealist:
            if flag:
                post_area = tmparea
                break
            elif area.id == tmparea.id:
                flag = True
            else:
                prev_area = tmparea
        
        url_base = UrlMaker.scout()
        # 前のエリア.
        if prev_area:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_AREA, prev_area.id)
            self.html_param['url_area_prev'] = self.makeAppLinkUrl(url)
        # 次のエリア.
        if post_area:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_AREA, post_area.id)
            self.html_param['url_area_next'] = self.makeAppLinkUrl(url)
        
        # カードの上限チェック.
        if v_player.cardlimit <= BackendApi.get_cardnum(uid, arg_model_mgr=model_mgr, using=using):
            self.__putParam('overlimit_card', True)
        
        # 宝箱の上限チェック.
        overlimit_treasure_list = BackendApi.get_treasuretype_list_overlimit(model_mgr, uid, using=using)
        self.__putParam('overlimit_treasure', overlimit_treasure_list)
        
        BackendApi.save_lastview_areaid(uid, areaid)

        # スキップフラグ
        self.__putParam('flag_skip', BackendApi.get_scoutskip_flag(uid))
        
        # レイドイベント.
        BackendApi.put_raidevent_champagnedata(self, uid)
        raideventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        if raideventmaster and raideventmaster.flag_dedicated_stage:
            self.html_param['url_raidevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.raidevent_scouttop())
        
        # スカウトイベント.
        scouteventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
        if scouteventmaster:
            scouteventconfig = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
            self.html_param['scoutevent'] = Objects.scouteventmaster(self, scouteventmaster, scouteventconfig)
            self.html_param['url_scoutevent_top'] = self.makeAppLinkUrl(UrlMaker.scoutevent_top(scouteventmaster.id))

        # プロデュースイベント.
        produceeventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
        if produceeventmaster:
            produceeventconfig = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
            self.html_param['produceevent'] = Objects.produceevent(self, produceeventmaster, produceeventconfig)
            self.html_param['url_produceevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.produceevent_scouttop())
        
        self.writeAppHtml('scout/scout')

def main(request):
    return Handler.run(request)
