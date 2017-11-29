# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler


class Handler(GachaHandler):
    """シンプルHTMLページ.
    """
    
    HTMLTABLE = {
        'gachaboxinfo' : 'gacha/box_info',
        'gachassrinfo' : 'gacha/ssr_info',
        'reddragon' : 'promotion/r_dragon/campaign',
    }
    
    def process(self):
        self.getViewerPlayer()
        
        args = self.getUrlArgs('/simple/')
        target = args.get(0)
        
        htmlname = Handler.HTMLTABLE.get(target)
        if htmlname is None:
            self.response.set_status(404)
            self.response.end()
            return
        
        self.writeAppHtml(htmlname)

def main(request):
    return Handler.run(request)
