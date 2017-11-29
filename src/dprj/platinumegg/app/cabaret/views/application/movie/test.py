# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """動画で試したいことをここでやる.
    """
    
    def process(self):
        self.response.set_header('Content-Type', 'application/x-mpegurl')
        template = OSAUtil.template_lockup.get_template('test/testmedia')
        data = template.render_unicode(url_media=self.url_media).encode(self.osa_util.write_enc, 'replace')
        self.response.send(data)

def main(request):
    return Handler.run(request)

