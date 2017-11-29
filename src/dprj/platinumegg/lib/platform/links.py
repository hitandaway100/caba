# -*- coding: utf-8 -*-
import urllib2
from platinumegg.lib.opensocial.util import OSAUtil


class Links:
    
    @classmethod
    def _makeLinkUrl(cls, osa_util, left, url, do_html_encode, do_quote=True):
        dest = url
        if (not osa_util.is_direct_access) and do_quote:
            dest = left + urllib2.quote(dest, '/')
        if do_html_encode:
            dest = OSAUtil.htmlEncode(dest)
        return dest
    
    @classmethod
    def makeLinkUrl(cls, osa_util, url, do_quote=True):
        """ページ遷移用url.
        """
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
        return cls.makeLinkUrl(osa_util, src, True, do_quote)
    @classmethod
    def makeLinkUrlSwfEmbed(cls, osa_util, src):
        """ページ内埋め込みFlashのURL.
        """
        return cls.makeLinkUrlAbsolute(osa_util, src)

