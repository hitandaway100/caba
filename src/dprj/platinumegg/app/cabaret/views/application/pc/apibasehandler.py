# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from defines import Defines
from django.db import close_connection
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib.pljson import Json

class ApiBaseHandler(AppHandler):
    """Apiのハンドラ.
    """
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def processError(self, error_message):
        # エラー起きた時の処理.
        if settings_sub.IS_BENCH:
            # 負荷テスト時は何かあった時にわかりやすくするため500返す.
            self.response.set_status(500)
        self.json_param['error_message'] = unicode(error_message)
        if settings_sub.USE_LOG:
            self.json_param['log'] = self.osa_util.logger.to_string()
        try:
            self.writeAppJson()
        except:
            aaa = {}
            aaa[Defines.STATUS_KEY_NAME] = CabaretError.Code.UNKNOWN
            aaa['error_message'] = u'json convert error.\r\n'
            aaa['error_message'] += unicode(self.json_param)
            aaa['result'] = {}
            if getattr(self, 'osa_util', None) is None:
                # __setStaticParamあたりで死ぬとosa_utilがセットされてない.
                self.__write_json_obj(aaa)
            else:
                self.osa_util.write_json_obj(aaa)
    
    def processAppError(self, err):
        self.json_param['error'] = {
            'code' : err.code,
            'str_code' : CabaretError.getCodeString(err.code),
            'message' : err.value,
        }
        self.json_param[Defines.STATUS_KEY_NAME] = err.code
        self.processError(err.value)
    
    def __write_json_obj(self, dict_data):
        """jsonレスポンス.
        """
        close_connection()
        json_data = StrUtil.to_s(Json.encode(dict_data))
        json_data = json_data.replace(': ',':').replace(', ',',')
        json_data = json_data.replace('\\r','')
        self.response.headers['Content-Type'] = 'application/json;'
        self.response.send(json_data)
