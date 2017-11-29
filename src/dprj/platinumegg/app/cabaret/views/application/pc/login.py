# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.platform import dmmpc
from Crypto.PublicKey import RSA
from oauth import oauth
import base64
import hashlib
import urllib
import binascii
import settings
import settings_sub

class Handler(AppHandler):
    """セッションを返す.
    """
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        AppHandler.checkUser(self)
        
        if settings_sub.IS_LOCAL:
            return
        
        # 署名の検証を行う.
        # RSA公開鍵を生成する
        if self.osa_util.appparam.sandbox:
            cert = dmmpc.api.CERT_DEV
        else:
            cert = dmmpc.api.CERT_REL
        exponent = 65537
        public_key_long = long(cert, 16)
        public_key = RSA.construct((public_key_long, long(exponent)))
        
        parameters = {}
        for k,v in self.request.django_request.GET.items():
            parameters[k] = urllib.unquote(v)
        
        # クエリパラメータをつなげてハッシュを生成する
        oauth_request = oauth.OAuthRequest.from_request(
            self.request.method,
            self.request.url,
            parameters=parameters)
        signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        _, raw = signature_method.build_signature_base_string(oauth_request, oauth.OAuthConsumer('dmm', ''), None)
        local_hash = hashlib.sha1(raw).digest()
        
        # シグネチャをBase64でデコードして公開鍵で複合化する
        oauth_request.parameters['oauth_signature'] = self.request.django_request.GET['oauth_signature']
        sig = base64.decodestring(urllib.unquote(oauth_request.get_parameter("oauth_signature")))
        remote_hash = public_key.encrypt(sig, '')[0][-20:]
        
        self.osa_util.logger.trace('local_hash :%s' % binascii.b2a_hex(local_hash))
        self.osa_util.logger.trace('remote_hash:%s' % binascii.b2a_hex(remote_hash))
        
        if local_hash == remote_hash:
            self.osa_util.logger.trace('rsa_sha1_check_ok?:True')
        else:
            self.osa_util.logger.trace('rsa_sha1_check_ok?:False')
            raise CabaretError(u'署名を確認できません', code=CabaretError.Code.OAUTH_ERROR)
    
    def process(self):
        self.json_param['session'] = self.osa_util.session
        self.json_param['viewer_id'] = self.osa_util.viewer_id
        self.json_param['app_id'] = self.osa_util.appparam.app_id
        self.json_param['code'] = CabaretError.Code.OK
        self.json_param['str_code'] = 'OK'
        
        v_player = self.getViewerPlayer(quiet=True)
        if v_player is None:
            # 初回アクセス.
            v_player = BackendApi.install(self)
        self.json_param['user_id'] = v_player.id
        self.response.set_status(200)
        self.writeAppJson()
    
    def processError(self, error_message):
        # なんかｴﾗｰ.
        self.response.clear()
        self.response.set_status(500)
        self.response.end()
    
    def processAppError(self, err):
        self.json_param['viewer_id'] = self.osa_util.viewer_id
        self.json_param['app_id'] = self.osa_util.appparam.app_id
        self.json_param['code'] = err.code
        self.json_param['str_code'] = CabaretError.getCodeString(err.code)
        self.json_param['message'] = err.value
        if err.code == CabaretError.Code.OAUTH_ERROR:
            self.response.set_status(401)
        else:
            self.response.set_status(200)
        self.writeAppJson()
    
    def checkMaintenance(self):
        """メンテナンスチェック.
        """
        model_mgr = self.getModelMgr()
        app_config = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        if app_config.is_maintenance():
            raise CabaretError(u'メンテナンス中です', CabaretError.Code.MAINTENANCE)
        return True
    
    def checkUserAgent(self):
        """UserAgentをチェック.
        """
        return True
    
def main(request):
    return Handler.run(request)
