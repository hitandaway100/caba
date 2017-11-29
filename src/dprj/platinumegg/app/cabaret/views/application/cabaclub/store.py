# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.util.redisdb import CabaClubRecentlyViewedTime
from collections import Counter

class Handler(CabaClubHandler):
    """キャバクラ経営店舗詳細.
    """
    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        if BackendApi.check_cabaclub_lead_resultanim(model_mgr, uid, self.__now, using=settings.DB_READONLY):
            # 結果演出へ.
            self.setFromPage(Defines.FromPages.CABACLUB_STORE)
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubresultanim()))
            return
        # 店舗のマスターデータ.
        args = self.getUrlArgs('/cabaclubstore/')
        self.__ctype = int(self.request.get(Defines.URLQUERY_CTYPE, 0))
        master_list = BackendApi.get_cabaretclub_store_master_all(model_mgr, using=settings.DB_READONLY)
#         storeset_dict = BackendApi.get_cabaretclub_storeset_dict(model_mgr, uid, [master.id for master in master_list], using=settings.DB_READONLY)
#         master_list.sort(key=lambda x:storeset_dict[x.id].playerdata.rtime if storeset_dict.get(x.id) else OSAUtil.get_datetime_max())
        master_id_list = [master.id for master in master_list]
        
        mid = args.getInt(0)
        master = None
        if mid and mid in master_id_list:
            master = master_list[master_id_list.index(mid)]
        if master is None:
            # 指定がない場合は最後に見た店舗.
            master = self.getLastViewedStoreMaster() or master_list[0]
        mid = self.__mid = master.id

        # 店舗のページング.
        master_num = len(master_id_list)
        if 1 < master_num:
            current_index = master_id_list.index(mid)
            self.html_param.update(
                url_prev = self.makeAppLinkUrl(UrlMaker.cabaclubstore(master_id_list[(current_index + master_num- 1) % master_num])),
                url_next = self.makeAppLinkUrl(UrlMaker.cabaclubstore(master_id_list[(current_index + 1) % master_num])),
            )
        # 店舗の更新.
        self.updateStore(self.__now, master)
        # 店舗情報.
        storeset = BackendApi.get_cabaretclub_storeset(model_mgr, uid, mid, using=settings.DB_READONLY)
        if storeset is None or not storeset.is_alive(self.__now):
            # レンタル画面.
            self.__process_rental(master)
        else:
            # 店舗画面.
            self.__process_store(storeset)
    
    def __process_rental(self, cabaclubstoremaster):
        """レンタル画面.
        """
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 店舗マスターをテンプレート向けに変換.
        obj_cabaclubstoremaster = Objects.cabaclubstoremaster(self, cabaclubstoremaster)
        # スコア情報.
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_READONLY)
        # HTML書き込み.
        self.html_param.update(
            cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata),
            cabaclubstoremaster = obj_cabaclubstoremaster,
        )
        self.writeAppHtml('cabaclub/store_rental')
    
    def __process_store(self, cabaclub_store_set):
        """店舗画面.
        """
        uid = cabaclub_store_set.playerdata.uid
        store_mid = cabaclub_store_set.master.id
        if cabaclub_store_set.playerdata.is_open and cabaclub_store_set.get_current_eventmaster(self.__now):
            # 最後に閲覧した時間.
            data = CabaClubRecentlyViewedTime.get(uid, store_mid)
            if data and data.vtime < cabaclub_store_set.playerdata.etime:
                # 前回見たのがイベント発生前.
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubeventanim(store_mid)))
                return
        # 店舗情報.
        obj_cabaclubstore = Objects.cabaclubstore(self, cabaclub_store_set, self.__now)
        # アイテム.
        obj_cabaclubitemdata = Objects.cabaclubitemdata(self, cabaclub_store_set, self.__now)
        # 配置されているキャスト.
        cardlist = self.getStoreCastList(store_mid)

        # 経営スキル
        cardlist_has_skill = BackendApi.filter_has_cabaclubskill(cardlist)
        cabaclub_skills = Counter()
        if cardlist_has_skill:
            for card in cardlist_has_skill:
                skill = card.master.getSkill()
                cabaclub_skills[skill.name] += 1
        self.html_param['cabaclub_skills'] = cabaclub_skills

        obj_cardlist = []
        for card in cardlist:
            obj_card = Objects.card(self, card)
            obj_card['url_change'] = self.makeAppLinkUrl(UrlMaker.cabaclubcastselect(store_mid, card.id))
            obj_card['url_remove'] = self.makeAppLinkUrl(UrlMaker.cabaclubcastremove(store_mid, card.id))
            obj_cardlist.append(obj_card)
        # キャスト追加リンク.
        url_addmember = None
        if len(cardlist) < cabaclub_store_set.master.cast_num_max:
            url_addmember = self.makeAppLinkUrl(UrlMaker.cabaclubcastselect(store_mid))

        # 店舗に設定可能なキャストを習得する
        setable_cardlist = BackendApi.get_cabaclub_setable_cardlist(self.getModelMgr(), uid, self.__now, using=settings.DB_READONLY)

        # HTML書き込み.
        url = UrlMaker.cabaclubdeckselect(self.__mid)
        self.html_param.update(
            cabaclubstore = obj_cabaclubstore,
            cabaclubitemdata = obj_cabaclubitemdata,
            cardlist = obj_cardlist,
            url_addmember = url_addmember,
            ctype = self.__ctype,
            cast_set = True if cardlist else False,
            cast_add = True if setable_cardlist else False,
            url_cabaclub_deckselect_add = self.makeAppLinkUrl(url),
            url_cabaclub_deckselect_remove = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_REM, 'rem')),
        )
        if cabaclub_store_set.playerdata.is_open:
            # 閲覧時間の更新.
            CabaClubRecentlyViewedTime.create(uid, store_mid, self.__now).save()
            self.writeAppHtml('cabaclub/store_opened')
        else:
            # 使用できるアイテム.
            self.setFromPage(Defines.FromPages.CABACLUB_STORE, store_mid)
            BackendApi.put_cabaclubitem_uselead_info(self, cabaclub_store_set, self.__now)
            self.writeAppHtml('cabaclub/store_closed')
    

def main(request):
    return Handler.run(request)
