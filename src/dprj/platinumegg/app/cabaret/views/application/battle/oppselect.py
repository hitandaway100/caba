# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import random
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub

class Handler(BattleHandler):
    """対戦相手更新.
    対戦相手が未設定の場合は回数消費なしで更新.
    対戦相手が設定済のときは回数を消費.
    回数をチェック.
    対戦相手を検索.
        見つからない時はエラー？
    対戦相手更新書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp]
    
    def process(self):
        
        def allEnd(url, err=None):
            if err and settings_sub.IS_LOCAL:
                raise err
            else:
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
        
        try:
            args = self.getUrlArgs('/battleoppselect/')
            postcnt = int(args.get(0))
        except:
            allEnd(UrlMaker.battle(), CabaretError(u'引数が正しくありません', CabaretError.Code.ILLEGAL_ARGS))
            return
        
        battleplayer = self.getBattlePlayer(get_instance=False)
        
        pre_o_player = None
        if battleplayer and battleplayer.opponent:
            arr = BackendApi.get_players(self, [battleplayer.opponent], [], using=settings.DB_READONLY)
            if arr:
                pre_o_player = arr[0]
        
        if pre_o_player is None:
            postcnt = 0
            do_remove_count = False
            opplist = []
        else:
            if postcnt == battleplayer.change_cnt:
                # 書き込み済み.
                allEnd(UrlMaker.battlepre(), CabaretError(u'設定済みです', CabaretError.Code.ALREADY_RECEIVED))
                return
            elif postcnt != (battleplayer.change_cnt + 1):
                # 想定外.
                allEnd(UrlMaker.battle(), CabaretError(u'引数が正しくありません', CabaretError.Code.ILLEGAL_ARGS))
                return
            opplist = battleplayer.rankopplist[:]
            do_remove_count = True
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        excludes = [v_player.id]
        excludes.extend(opplist)
        excludes.extend(BackendApi.get_friend_idlist(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY))
        
        arr = BackendApi.get_battleopponents_by_levelband(v_player.level, num=1, excludes=excludes)
        oid = None
        if arr:
            oid = arr[0]
        else:
            if battleplayer:
                while battleplayer.opponent in opplist:
                    opplist.remove(battleplayer.opponent)
            # 見つからなかったので戦ったことのある人を設定しておこう..
            if opplist:
                oid = random.choice(opplist)
        if oid is None:
            # ここは...
            raise CabaretError(u'対戦相手が見つかりませんでした', CabaretError.Code.NOT_DATA)
        
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, oid, postcnt, do_remove_count)
            model_mgr.write_end()
        except Exception, err:
            allEnd(UrlMaker.battle(), err)
            return
        
        if settings_sub.IS_BENCH:
            self.response.end()
        else:
            allEnd(UrlMaker.battlepre())
    
    @staticmethod
    def tr_write(uid, oid, post_cnt, do_remove_count):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_update_battle_opponent(model_mgr, uid, oid, post_cnt, do_remove_count)
        model_mgr.write_all()
        return model_mgr
    

def main(request):
    return Handler.run(request)
