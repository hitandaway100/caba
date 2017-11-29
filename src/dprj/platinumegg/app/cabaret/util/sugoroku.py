# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusSugorokuPlayerData
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from random import randint
from collections import namedtuple
import settings_sub

class Sugoroku:
    """双六.
    """
    SugorokuResult = namedtuple('SugorokuResult', 'number,squares_master_list,prizes')
    
    def __init__(self, backend_api, model_mgr, loginbonusmaster, playdata=None):
        self.__backend_api = backend_api
        self.__model_mgr = model_mgr
        self.__loginbonusmaster = loginbonusmaster
        self.__playdata = playdata or LoginBonusSugorokuPlayerData.makeInstance(0)
    @property
    def backend_api(self):
        return self.__backend_api
    @property
    def model_mgr(self):
        return self.__model_mgr
    @property
    def loginbonusmaster(self):
        return self.__loginbonusmaster
    
    def play(self, test=False):
        """双六ログインボーナス実行.
        """
        prizes = {}
        def add_prize(prizelist, textid):
            """報酬を追加.
            """
            arr = prizes[textid] = prizes.get(textid) or []
            arr.extend(prizelist)
        
        model_mgr = self.model_mgr
        master = self.loginbonusmaster
        # 現在のマップ.
        loc_pre = self.__playdata.loc
        number = 0
        # 停まったマス.
        stopped_queue = []
        if 0 < self.__playdata.lose_turns:
            # 休み中.
            self.__playdata.lose_turns -= 1
        else:
            mapid = master.getMapIDByLap(self.__playdata.lap)
            # 現在のマスの情報.
            current_squares_master = self.backend_api.get_loginbonus_sugoroku_map_squares_master(model_mgr, mapid, loc_pre, using=settings.DB_READONLY)
            if current_squares_master.last:
                # ここは最終マス.
                mapmaster = self.backend_api.get_loginbonus_sugoroku_map_master(model_mgr, mapid, using=settings.DB_READONLY)
                if not mapmaster.prize:
                    return None
                # 達成済み報酬獲得.
                prizelist = self.backend_api.get_prizelist(model_mgr, mapmaster.prize)
                add_prize(prizelist, mapmaster.prize_text)
            else:
                # サイコロを回す.
                GO_COUNT_MAX = 10   # 変なデータが設定されていた時用.
                def go(queue, loc, number, cnt=0):
                    def _go(mapid, cur_loc, number):
                        # マスの情報を取得.
                        loc_post = cur_loc + number
                        squares_master_list = self.backend_api.get_loginbonus_sugoroku_map_squares_master_by_mapid(model_mgr, mapid, cur_loc+1, loc_post, using=settings.DB_READONLY)
                        # 止まる場所を探す.
                        target_squares_master = None
                        max_number = cur_loc
                        for squares_master in squares_master_list:
                            max_number = max(max_number, squares_master.number)
                            if squares_master.last:
                                # 最終マス.
                                target_squares_master = squares_master
                            elif squares_master.number == loc_post:
                                # 停まったマス.
                                target_squares_master = squares_master
                        return target_squares_master, loc_post - max_number
                    mapid = master.getMapIDByLap(self.__playdata.lap)
                    rest = number
                    for _ in xrange(number):    # while Trueじゃなくて出目分だけループ.
                        target_squares_master, rest = _go(mapid, loc, rest)
                        if target_squares_master or rest < 1:
                            # 停まった.
                            break
                        if 1 < len(master.maps):
                            # 次のマップへ.
                            self.__playdata.lap += 1
                            mapid = master.getMapIDByLap(self.__playdata.lap)
                        # スタート地点から.
                        loc = 0
                    if target_squares_master is None:
                        raise CabaretError(u'止まる場所が見つからなかった', code=CabaretError.Code.INVALID_MASTERDATA)
                    def stop(target_squares_master, cnt):
                        if GO_COUNT_MAX <= cnt:
                            raise CabaretError(u'イベントが実行されすぎ', code=CabaretError.Code.INVALID_MASTERDATA)
                        queue.append(target_squares_master)
                        mapid = master.getMapIDByLap(self.__playdata.lap)
                        if target_squares_master.prize:
                            # 停まった時の報酬.
                            prizelist = self.backend_api.get_prizelist(model_mgr, target_squares_master.prize)
                            add_prize(prizelist, target_squares_master.prize_text)
                        if not target_squares_master.last:
                            # 最終マスじゃない場合はイベント発生.
                            if target_squares_master.event_type == Defines.SugorokuMapEventType.GO:
                                # 進む.
                                go(queue, target_squares_master.number, target_squares_master.event_value, cnt + 1)
                            elif target_squares_master.event_type == Defines.SugorokuMapEventType.BACK:
                                # 戻る.
                                loc = target_squares_master.number - target_squares_master.event_value
                                if loc < 1 and 0 < self.__playdata.lap:
                                    # 2周目以降はスタート地点より後ろに戻る.
                                    self.__playdata.lap -= 1
                                    mapid = master.getMapIDByLap(self.__playdata.lap)
                                    target_squares_master = self.backend_api.get_loginbonus_sugoroku_map_squares_master_by_mapid(model_mgr, mapid, using=settings.DB_READONLY)[-1]
                                else:
                                    # 1周目はスタート地点より後ろには戻らない.
                                    target_squares_master = self.backend_api.get_loginbonus_sugoroku_map_squares_master(model_mgr, mapid, max(1, loc), using=settings.DB_READONLY)
                                # 停まった時の処理.
                                stop(target_squares_master, cnt + 1)
                            elif target_squares_master.event_type == Defines.SugorokuMapEventType.LOSE_TURN:
                                # 休み.
                                self.__playdata.lose_turns = target_squares_master.event_value
                            elif target_squares_master.event_type == Defines.SugorokuMapEventType.JUMP:
                                # 飛ぶ.
                                loc = target_squares_master.event_value
                                target_squares_master = self.backend_api.get_loginbonus_sugoroku_map_squares_master(model_mgr, mapid, loc, using=settings.DB_READONLY)
                                if target_squares_master is None:
                                    raise CabaretError(u'飛び先が存在しない', code=CabaretError.Code.INVALID_MASTERDATA)
                                # 停まった時の処理.
                                stop(target_squares_master, cnt + 1)
                    stop(target_squares_master, cnt)
                # サイコロを振る.
                number = randint(1, 6) if not (test and settings_sub.IS_LOCAL) else 6
                # 出た目の分だけ進む.
                go(stopped_queue, loc_pre, number)
                # 最終的に停まったマス.
                stopped_squares_master = stopped_queue[-1]
                self.__playdata.loc = stopped_squares_master.number
        return Sugoroku.SugorokuResult(number, stopped_queue, prizes)
    