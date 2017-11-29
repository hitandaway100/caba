# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """ライフサイクルイベント.
    """
    KEY_EVENT_TYPE = u'eventtype'
    KEY_ID = u'id'
    KEY_INVITE_FROM_ID = u'invite_from_id'
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        pass
    
    def check_process_pre(self):
        return True
    
    def processError(self, error_message):
        self.osa_util.logger.error(error_message)
        self.response.set_status(500)
        self.response.end()
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/lifecycle/')
        
        procname = args.get(0)
        table = {
            'addapp' : self.procAddapp,
            'removeapp' : self.procRemoveapp,
        }
        proc = table.get(procname, None)
        if proc is None:
            # 不正リクエスト.
            self.response.set_status(400)
            self.response.end()
        else:
            proc()
    
    def procAddapp(self):
        """ゲーム開始.
        """
        self._now = OSAUtil.get_now()
        eventtype = self.request.get(self.KEY_EVENT_TYPE)
        if eventtype != 'event.addapp':
            # 不正リクエスト.
            self.response.set_status(400)
            self.response.end()
            return
        
        dmm_invite_id = self.request.get(self.KEY_ID)
        dmm_invite_from_id = self.request.get(self.KEY_INVITE_FROM_ID)
        if dmm_invite_from_id == None:
#            f = None
#            try:
#                arr = []
#                arr.append(OSAUtil.get_now().strftime("[%Y/%m/%d %H:%M:%S]"))
#                arr.append("id=%s" % dmm_invite_id)
#                arr.append("invite_from_id=%s" % dmm_invite_from_id)
#                arr.append('request headers:')
#                arr.extend(['\t%s: %s' % (k,v) for k,v in self.request.headers.items()])
#                arr.append("body=%s" % self.request.django_request.raw_post_data)
#                arr.append('\n')
#                
#                f = open(os.path.join(settings_sub.ERR_LOG_PATH, 'addapp.log'), 'a')
#                f.write('\n'.join(arr))
#                f.close()
#                f = None
#            except Exception, err:
#                print err
#                if f:
#                    f.close()
#                raise
            # 招待者の指定がない場合正常応答.
            self.response.set_status(200)
            self.response.end()
            return
        
        invite_from_id= BackendApi.dmmid_to_appuid(self, [dmm_invite_from_id], using=settings.DB_READONLY)
        if len(invite_from_id) <= 0:
            # 未登録ユーザからの招待は何もしないで正常応答.
            self.response.set_status(200)
            self.response.end()
            return
        
        idlist = list(set(dmm_invite_id.split(',')))
        result = BackendApi.tr_invite_add(self, idlist, invite_from_id[dmm_invite_from_id])
        if result:
            self.response.set_status(200)
        self.response.send()
    
    def procRemoveapp(self):
        """ゲーム終了.
        """
        self.response.set_status(200)
        self.response.send()

def main(request):
    return Handler.run(request)
