# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Card import CardMaster, CardSortMaster
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.lib.opensocial.util import OSAUtil
import settings_sub


class Handler(AppHandler):
    """
        一括で配属できる機能

        条件
            - キャスト編成でキャバ道に編成されていない
            - キャスト編成で超太客に編成されていない
            - 経営で選択中の店舗以外に配属されていない

        上記条件に該当するキャストの中で属性を指定して自動で配属できるようにします。
        必要な属性は、すべて、魔、知、癒の4つです。
        バトルと違って接客力を使っていないので、レア度と人件費を見て、双方が揃って高いものを優先して配属します。
        また、その中でも経営スキルを持っているものがさらに優先で配属されます。
        完全に条件が被ってしまった場合は、カードIDを見て、若い番号を優先する。
    """

    def process(self):
        # 現在時刻.
        self.__now = OSAUtil.get_now()

        args = self.getUrlArgs('/cabaclubdeckselect/')

        # Retrieve the necessary arguments
        # mid : Cabaclubstore id
        # card_type : (全て、悪、知、癒) as defined in Defines.CharacterType.NAMES
        try:
            mid = args.getInt(0)
            card_type = int(self.request.get(Defines.URLQUERY_CTYPE, 0))
            is_remove = self.request.get(Defines.URLQUERY_REM, '') == "rem"
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)

        url = UrlMaker.cabaclubstore(mid=mid)

        # Automatically choose the casts and add them to the deck
        # for the Cabaclubstore of id `mid`
        if card_type:
            url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, card_type)

        # 一括編成 / 一括解除
        self.processAuto(mid, card_type, is_remove=is_remove)

        if settings_sub.IS_BENCH:
            self.response.set_status(200)
            self.response.end()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

    def processAuto(self, mid, card_type, is_remove=False):
        """自動設定.
        """

        def sort_fun(cardset):
            """This method sorts the cards in a cardset in the priority of
                Rarity > Cost > CabaclubSkill
                Cabaclub skill of the card must be of type Defines.SkillEffect.CABACLUB
            """
            cardsortmaster = cardset.master.getModel(CardSortMaster)
            cardmaster = cardset.master.getModel(CardMaster)
            skill = cardset.master.getSkill()
            if skill:
                return cardsortmaster.rare, cardmaster.cost, skill.eskill == Defines.SkillEffect.CABACLUB
            return cardsortmaster.rare, cardmaster.cost

        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        uid = v_player.id
        user_cardidlist = []
        storemaster = BackendApi.get_cabaretclub_store_master(model_mgr, mid, using=settings.DB_READONLY)

        if not is_remove:
            # 店舗に設定可能なキャストを習得する
            user_cardset = BackendApi.get_cabaclub_setable_cardlist(model_mgr, uid, self.__now, ctype=card_type, using=settings.DB_READONLY)
            # current cast in the deck of current Cabaclubstoremaster
            current_storemaster_castidlist = BackendApi.get_cabaretclub_castdata(model_mgr, uid, mid,using=settings.DB_READONLY)

            # get_cabaclub_setable_cardlist excludes the cards
            # that where set in the current store (even if the current store's status is closed).
            # We have to get those cards and include them back again
            # Why do we do that? Because there is a possibility that those cards follow the specification listed above
            if current_storemaster_castidlist:
                current_storemaster_cardset = BackendApi.get_cards(current_storemaster_castidlist.cast, model_mgr, using=settings.DB_DEFAULT)
                if card_type != Defines.CharacterType.ALL:
                    current_storemaster_cardset = [cardset for cardset in current_storemaster_cardset
                                                   if cardset.master.getModel(CardSortMaster).ctype == card_type]

                # add the cast already set in the current store to the user's cardset
                user_cardset.extend(current_storemaster_cardset)

            # まずはCardIDでソート
            user_cardset = sorted(user_cardset, key=lambda x:x.master.getModel(CardMaster).id)
            # レアリティ、人件費と経営スキルでソート
            # 優先度:　レアリティ > 人件費 > 経営スキル
            filtered_user_cardset = sorted(user_cardset, key=sort_fun, reverse=True)

            user_cardidlist = [cardset.id for cardset in filtered_user_cardset][:storemaster.cast_num_max]

        # デッキ変更書き込み.
        wrote_model_mgr = db_util.run_in_transaction(Handler.tr_write, uid, storemaster, self.__now, user_cardidlist)
        wrote_model_mgr.write_end()

    @staticmethod
    def tr_write(uid, cabaclubstoremaster, now, cardidlist):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_cabaclubstore_set_cast(model_mgr, uid, cabaclubstoremaster, cardidlist, now)
        model_mgr.write_all()
        return model_mgr


def main(request):
    return Handler.run(request)
