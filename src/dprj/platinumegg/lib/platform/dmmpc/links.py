# -*- coding: utf-8 -*-
from platinumegg.lib.platform.links import Links as base
from platinumegg.lib.opensocial.util import OSAUtil


class Links(base):
    
    @classmethod
    def makeLinkUrl(cls, osa_util, url, do_quote=True):
        """ページ遷移用url.
        """
        if osa_util.session:
            url = OSAUtil.addQuery(url, '_session', osa_util.session)
        return url
    @classmethod
    def makeLinkUrlActivity(cls, osa_util, callback_url):
        """アクティビティ送信用url.
        """
        return cls.makeLinkUrl(osa_util, callback_url)
    @classmethod
    def makeLinkUrlInvite(cls, osa_util, callback_url, body):
        """招待ページurl.
        """
        return cls.makeLinkUrl(osa_util, callback_url)
    @classmethod
    def makeLinkUrlDiary(cls, osa_util, callback_url=None, subject=None, body=None, image_url=None):
        """日記投稿用URL.
        """
        return cls.makeLinkUrl(osa_util, callback_url)
    @classmethod
    def makeLinkUrlLocation(cls, osa_util, callback_url, location_type='cell'):
        """位置情報取得用URL.
        """
        return cls.makeLinkUrl(osa_util, callback_url)
    @classmethod
    def makeLinkUrlAbsolute(cls, osa_util, url):
        """ 絶対パスでURLを作る.
        """
        return cls.makeLinkUrl(osa_util, url, False)
    @classmethod
    def makeLinkUrlRedirect(cls, osa_util, src):
        """ リダイレクト用URLの作成.
        """
        return cls.makeLinkUrlAbsolute(osa_util, src)
    @classmethod
    def makeLinkUrlBinary(cls, osa_util, src, do_quote=False):
        """リンク先がバイナリデータ(flash,画像等)のURL
        """
        return cls.makeLinkUrl(osa_util, src, True)
    @classmethod
    def makeLinkUrlSwfEmbed(cls, osa_util, src):
        """ページ内埋め込みFlashのURL.
        """
        return cls.makeLinkUrlAbsolute(osa_util, src)

