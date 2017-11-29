# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Infomation import PopupMaster

class PopupBanner():
    """ポップアップ.
    """
    
    def __init__(self, popupmaster, eventbannermaster):
        self.__popupmaster = popupmaster
        self.__eventbannermaster = eventbannermaster
    
    @property
    def banner(self):
        if self.__popupmaster.bannerflag and self.__eventbannermaster and self.__eventbannermaster.id == self.__popupmaster.banner:
            return self.__eventbannermaster
        else:
            return None
    
    def __getattr__(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        elif name in PopupMaster.get_column_names():
            return getattr(self.__popupmaster, name)
        else:
            raise AttributeError('PopupBanner instance do not have %s' % name)
