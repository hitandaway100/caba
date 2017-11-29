# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerAp,\
    PlayerExp, PlayerFriend
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings_sub
import urllib
from defines import Defines
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventScoutPlayData


class Handler(ProduceEventBaseHandler):
    """レイドイベントスカウト実行.
    引数:
        リクエストキー.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return []

    def redirectWithError(self, err):
        """ When an error occurs this method is called
            to redirect the user to the top page of Produce Event
        """
        url = self.makeAppLinkUrlRedirect(UrlMaker.produceevent_top())
        self.appRedirect(url)

    def process(self):

        args = self.getUrlArgs('/produceeventscoutdo/')
        try:
            scoutkey = urllib.unquote(args.get(1))

            # get the flag value of skipping animation from the url
            str_flag_skip = self.request.get(Defines.URLQUERY_SKIP)
            if not str_flag_skip in ('1', '0'):
                str_flag_skip = None

            # get the flag value for 全力探索 from the url
            str_flag_search = self.request.get(Defines.URLQUERY_SEARCH)
            if not str_flag_search in ('1', '0'):
                str_flag_search = None
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)

        model_mgr = self.getModelMgr()
        using = settings.DB_DEFAULT

        v_player = self.getViewerPlayer()
        uid = v_player.id

        # 演出スキップ
        if str_flag_skip:
            flag_skip = bool(int(str_flag_skip))
            BackendApi.set_scoutskip_flag(uid, flag_skip)
        else:
            flag_skip = BackendApi.get_scoutskip_flag(uid)

        # 全力探索フラグ
        if str_flag_search:
            flag_search = bool(int(str_flag_search))
            BackendApi.set_scoutsearch_flag(uid, flag_search)
        else:
            flag_search = BackendApi.get_scoutsearch_flag(uid)

        eventmaster = self.getCurrentProduceEvent()
        mid = eventmaster.id

        # プレイ情報
        playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, uid, using=using)

        # ステージマスターのマスターデータ
        stagemaster = BackendApi.get_current_produceeventstage_master(model_mgr, eventmaster, playdata, using=using)

        if scoutkey != playdata.alreadykey:
            try:
                model_mgr, playdata = db_util.run_in_transaction(self.tr_write, eventmaster, uid, stagemaster, scoutkey)
                model_mgr.write_end()
            except CabaretError, err:
                print "Error in scout/do.py :   ", err
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    model_mgr.delete_models_from_cache(
                        ProduceEventScoutPlayData,
                        [ProduceEventScoutPlayData.makeID(uid, mid)]
                    )
                elif err.code == CabaretError.Code.OVER_LIMIT:
                    # これ以上実行できない
                    url = UrlMaker.produceevent_top()
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
                else:
                    # うまく実行できない
                    if settings_sub.IS_DEV:
                        # マスターデータが正しくないとかあるだろうからソオのチェック用
                        raise
                    # ここに来るのは不正アクセス等のユーザという想定.
                    self.redirectWithError(CabaretError(u'閲覧できないエリアです', CabaretError.Code.ILLEGAL_ARGS))
                    return

        if flag_skip:
            url = UrlMaker.produceevent_scoutresultanim(stagemaster.id, scoutkey, 0)
        else:
            url = UrlMaker.produceevent_scoutanim(stagemaster.id, scoutkey)

        if settings_sub.IS_BENCH:
            self.response.end()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))

    def tr_write(self, eventmaster, uid, stagemaster, scoutkey):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_player(self, uid, [PlayerAp, PlayerExp, PlayerFriend], model_mgr=model_mgr)
        playdata = BackendApi.tr_do_produceevent_scout(model_mgr, eventmaster, player, stagemaster, scoutkey, self.is_pc, handler=self)
        model_mgr.write_all()
        return model_mgr, playdata


def main(request):
    return Handler.run(request)
