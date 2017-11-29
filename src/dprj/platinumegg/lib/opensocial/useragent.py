# -*- coding: utf-8 -*-
import re

class BrowserType:
    """ブラウザタイプ.
    """
    # スマホ.
    IPHONE = 'iPhone'
    IPOD = 'iPod'
    IPAD = 'iPad'
    ANDROID = 'Android'
    BRACKBERRY = 'BlackBerry'
    SYMBIAN = 'Symbian'
    INTERNETEXPROLER = 'MSIE'
    INTERNETEXPROLER_11_OVER = 'Trident'
    CHROME = 'Chrome'
    FIREFOX = 'Firefox'
    SAFARI = 'Safari'
    OPERA = 'Opera'
    OTHER = 'Other'
    
    SMARTPHONE = (IPHONE, ANDROID, BRACKBERRY, SYMBIAN)
    PC = (IPAD, INTERNETEXPROLER, INTERNETEXPROLER_11_OVER, CHROME, FIREFOX, SAFARI, OPERA)
    IOS = (IPHONE, IPOD, IPAD)

class UserAgent:
    
    IOS_USERAGENT_SAMPLE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53'
    
    regexp_ios_version = re.compile(r'.*OS (\d+)[.|_](\d+)[.|_]?(\d+)?')
    regexp_android_version = re.compile(r'.*Android (\d+).(\d+).?(\d+)?')
    regexp_ie_version = re.compile(r'.*MSIE (\d+).(\d+)?')
    regexp_ie11_version = re.compile(r'.*rv:(\d+).(\d+)?')
    regexp_chrome_version = re.compile(r'.*Chrome/(\d+).(\d+).(\d+)?')
    regexp_safari_version = re.compile(r'.*Version/(\d+).(\d+).(\d+)?')
    regexp_firefox_version = re.compile(r'.*Firefox/(\d+).(\d+)?')
    
    regexp_movieagent = re.compile(r'.*(stagefright|HTC Streaming Player|LG Player|SBHLS)')
    
    @staticmethod
    def make(useragent, supports=None):
        ins = UserAgent()
        
        ins.__data = useragent
        
        if supports is None:
            supports = list(BrowserType.SMARTPHONE) + list(BrowserType.PC)
        
        browsertype = None
        is_movie = False
        
        movie_mobj = UserAgent.regexp_movieagent.match(useragent)
        if movie_mobj:
            # Androidの動画プレイヤー.
            browsertype = BrowserType.ANDROID
            is_movie = True
        else:
            target = list(supports)[:]
            if BrowserType.IPHONE in supports:
                target.insert(0, BrowserType.IPAD)
                target.insert(0, BrowserType.IPOD)
            
            for btype in target:
                if useragent.find(btype) != -1:
                    browsertype = btype
                    break
        ins.is_movie = is_movie
        
        if browsertype and browsertype in supports:
            ins.browser = browsertype
        else:
            ins.browser = BrowserType.OTHER
        
        is_smartphone = ins.browser in BrowserType.SMARTPHONE
        
        version = None
        if ins.browser in BrowserType.IOS:
            mobj = UserAgent.regexp_ios_version.match(useragent)
            version = '.'.join(mobj.groups('0')) if mobj else '0.0.0'
            is_smartphone = ins.browser == BrowserType.IPHONE
        if ins.browser == BrowserType.ANDROID:
            mobj = UserAgent.regexp_android_version.match(useragent)
            if mobj:
                version = '.'.join(mobj.groups('0'))
            else:
                version = '0.0.0'
            is_smartphone = useragent.find('Mobile') != -1 or is_movie
        elif ins.browser == BrowserType.INTERNETEXPROLER:
            mobj = UserAgent.regexp_ie_version.match(useragent)
            version = '.'.join(mobj.groups('0')) if mobj else '0.0.0'
        elif ins.browser == BrowserType.INTERNETEXPROLER_11_OVER:
            mobj = UserAgent.regexp_ie11_version.match(useragent)
            version = '.'.join(mobj.groups('0')) if mobj else '0.0.0'
        elif ins.browser == BrowserType.CHROME:
            mobj = UserAgent.regexp_chrome_version.match(useragent)
            version = '.'.join(mobj.groups('0')) if mobj else '0.0.0'
        elif ins.browser == BrowserType.SAFARI:
            mobj = UserAgent.regexp_safari_version.match(useragent)
            version = '.'.join(mobj.groups('0')) if mobj else '0.0.0'
        elif ins.browser == BrowserType.FIREFOX:
            mobj = UserAgent.regexp_firefox_version.match(useragent)
            version = '.'.join(mobj.groups('0')) if mobj else '0.0.0'
        
        ins.version = version
        ins.__is_smartphone = is_smartphone
        
        is_windows = False
        if not is_smartphone and useragent.find('Win') != -1:
            is_windows = True
        ins.is_windows = is_windows
        
        return ins
    
    @property
    def data(self):
        return self.__data
    
    def is_pc(self):
        return self.browser in BrowserType.PC
    
    def is_smartphone(self):
        return self.__is_smartphone
    
    def is_ios(self):
        return self.browser in BrowserType.IOS
    
    def is_android(self):
        return self.browser == BrowserType.ANDROID

