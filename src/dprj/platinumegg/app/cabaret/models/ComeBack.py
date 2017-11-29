# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster, Singleton
from platinumegg.app.cabaret.models.base.fields import JsonCharField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID


class ComeBackCampaignMaster(BaseMaster):
    """カムバックキャンペーンのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前', help_text=u'アプリ内では使用しません')
    effectname = models.CharField(max_length=64, verbose_name=u'演出名', default='comeback_cp')
    interval = models.PositiveSmallIntegerField(default=0, verbose_name=u'空きの日数')
    prizetext = models.PositiveIntegerField(default=0, verbose_name=u'報酬の文言')
    prize_thumb_1 = models.CharField(default='', max_length=96, verbose_name=u'1日目の報酬画像')
    prize_1 = JsonCharField(default=list, verbose_name=u'1日目の報酬')
    prize_thumb_2 = models.CharField(default='', max_length=96, verbose_name=u'2日目の報酬画像')
    prize_2 = JsonCharField(default=list, verbose_name=u'2日目の報酬')
    prize_thumb_3 = models.CharField(default='', max_length=96, verbose_name=u'3日目の報酬画像')
    prize_3 = JsonCharField(default=list, verbose_name=u'3日目の報酬')
    prize_thumb_4 = models.CharField(default='', max_length=96, verbose_name=u'4日目の報酬画像')
    prize_4 = JsonCharField(default=list, verbose_name=u'4日目の報酬')
    prize_thumb_5 = models.CharField(default='', max_length=96, verbose_name=u'5日目の報酬画像')
    prize_5 = JsonCharField(default=list, verbose_name=u'5日目の報酬')
    prize_thumb_6 = models.CharField(default='', max_length=96, verbose_name=u'6日目の報酬画像')
    prize_6 = JsonCharField(default=list, verbose_name=u'6日目の報酬')
    prize_thumb_7 = models.CharField(default='', max_length=96, verbose_name=u'7日目の報酬画像')
    prize_7 = JsonCharField(default=list, verbose_name=u'7日目の報酬')
    
    def get_thumbnail(self, days):
        return getattr(self, 'prize_thumb_%d' % days, None)
    def get_prize(self, days):
        return getattr(self, 'prize_%d' % days, None)

class CurrentComeBackCampaignConfig(Singleton):
    """カムバックキャンペーンの設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    datalist = JsonCharField(default=list, verbose_name=u'設定内容')
    
    def setData(self, mid, stime, etime, idx=None):
        data = (mid, {'mid':mid,'stime':stime,'etime':etime})
        if idx is None:
            datadict = dict(self.datalist)
            # 順番を未指定.
            if datadict.has_key(mid):
                # 既存のものを上書き.
                datadict[mid].update(data[1])
            else:
                # 無いので新規.
                self.datalist.append(data)
        else:
            # 場所を指定.
            arr = []
            flag = False
            for _data in self.datalist:
                if len(arr) == idx:
                    arr.append(data)
                    flag = True
                if _data[0] == mid:
                    pass
                else:
                    arr.append(_data)
            if not flag:
                arr.append(data)
            self.datalist = arr
    
    def getData(self, idx=0):
        if idx < len(self.datalist):
            return self.datalist[idx][1]
        else:
            return None
    
    def getDataList(self):
        return self.datalist

class ComeBackCampaignData(BasePerPlayerBaseWithMasterID):
    """カムバックキャンペーンのユーザーデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    days = models.PositiveSmallIntegerField(default=0, verbose_name=u'現在のカムバック日数')
    comeback = models.BooleanField(default=False, verbose_name=u'受取可能フラグ')
