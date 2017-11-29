# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings


class Handler(AppHandler):
    """アイテム使用確認.
    表示するもの.
        アイテム情報.
        使用前後の所持数.
        使った結果.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/item_usecomplete/')
        try:
            mid = int(args.get(0, 0))
            errcode = int(args.get(1, 0))
            before_num = int(args.get(2, 0))
            after_num = int(args.get(3, 0))
            difference_value = int(args.get(5, 0)) - int(args.get(4, 0))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        is_duplicate = False
        is_not_enough = False
        is_overlimit = False
        is_error = True
        
        if errcode == CabaretError.Code.OK:
            is_error = False
        elif errcode == CabaretError.Code.ALREADY_RECEIVED:
            is_duplicate = True
        elif errcode == CabaretError.Code.NOT_ENOUGH:
            is_not_enough = True
        elif errcode == CabaretError.Code.OVER_LIMIT:
            is_overlimit = True
        
        self.html_param['mid'] = mid
        self.html_param['is_error'] = is_error
        self.html_param['is_duplicate'] = is_duplicate
        self.html_param['is_not_enough'] = is_not_enough
        self.html_param['before_num'] = before_num
        self.html_param['after_num'] = after_num
        self.html_param['difference_value'] = difference_value
        self.html_param['is_overlimit'] = is_overlimit
        
        self.putFromBackPageLinkUrl()
        
        # 使用するアイテム情報.
        model_mgr = self.getModelMgr()
        master = BackendApi.get_itemmaster(model_mgr, mid, using=settings.DB_READONLY)
        self.html_param['item'] = Objects.item(self, master, after_num)
        
        self.writeAppHtml('item/usecomplete')

def main(request):
    return Handler.run(request)
