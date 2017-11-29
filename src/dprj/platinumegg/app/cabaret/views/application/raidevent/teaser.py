# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler

class Handler(AppHandler):
    """ティザーページ.
    """
    
    def process(self):
        args = self.getUrlArgs('/raideventteaser/')
        eventhtmlname = '/'.join([args.get(i) for i in xrange(args.length()) if args.get(i)])
        self.writeAppHtml('%s/teaser_info' % eventhtmlname)

def main(request):
    return Handler.run(request)
