# -*- coding: utf-8 -*-

from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """n周年記念トップページ"""

    def process(self):
        args = self.getUrlArgs('/anniv/')
        anniv_type = args.get(0, '3rd')
        now = OSAUtil.get_now()

        self.html_param['now'] = now
        self.html_param['strToDateTime'] = DateTimeUtil.strToDateTime
        self.html_param['makeAppLinkUrl'] = self.makeAppLinkUrl

        anniv_name = '{}_anniv'.format(anniv_type)
        self.html_param['anniv_name'] = anniv_name

        self.writeAppHtml('anniv/{}/top'.format(anniv_type))


def main(request):
    return Handler.run(request)
