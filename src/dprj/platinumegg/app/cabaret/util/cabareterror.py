# -*- coding: utf-8 -*-
from platinumegg.lib.apperror import AppError


class CabaretError(AppError):
    """アプリケーションエラー.
    """
    class Code:
        (
            OK,                   # OK.エラーなのにOKっておかしいけどまぁOK.
        ) = xrange(0x000, 0x000+1)
        
        # API共通そうなの.
        (
            SERVER_BUSY,            # サーバーが忙しい.
            RESTART,                # 再起動して下さい.
            MAINTENANCE,            # メンテナンスモード中.
            INVALID_SESSION,        # セッション認証できない.
            ILLEGAL_ARGS,           # 引数が正しくない.
            OAUTH_ERROR,            # oauth認証エラー.
            
            TOO_MANY_TRANSACTION,   # transaction数が限界.
            NOT_AUTH,               # 管理ページ認証されていない.
            NOT_ALLOWED_IP,         # 許可されていないIP（管理画面用）.
            
            INVALID_MASTERDATA,     # マスターデータが不正.
            
            NOT_SUPPORT,            # 非対応.
        ) = xrange(0x100, 0x100+11)
        
        # 場面ごとに判定してね.
        (
            NOT_REGISTERD,
            NOT_DATA,
            ALREADY_RECEIVED,
            OVER_LIMIT,
            NOT_ENOUGH,
            EVENT_CLOSED,
        ) = xrange(0x200, 0x200+6)
        
        # 不明のエラー.
        UNKNOWN = AppError.STATUS_UNKNOWN
        
        # 開発者だけ見えていればいいエラー.
        DEVELOPER_ONLY = (
            TOO_MANY_TRANSACTION,   # transaction数が限界.
            UNKNOWN,
        )
        
        # ログに残したいエラー.
        LEAVE_LOG = (
            SERVER_BUSY,
            TOO_MANY_TRANSACTION,
            UNKNOWN,
        )
    #=========================================================
    # アプリごとに実装.
    def _isDeveloperOnlyStatus(self):
        return self.code in CabaretError.Code.DEVELOPER_ONLY
    
    @classmethod
    def getCodeString(cls, code):
        # そのコードの文字列.
        if code is None:
            return 'None'
        
        for k,v in CabaretError.Code.__dict__.items():
            if code == v:
                return  k
        return ''
