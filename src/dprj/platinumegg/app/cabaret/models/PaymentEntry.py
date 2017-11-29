# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.fields import AppDateTimeField


class PaymentEntry(BaseModel):
    """課金レコード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = True
    
    FIXED_COLUMNS = (
        'uid','iid','inum','price'
    )
    
    id = models.CharField(max_length=64, primary_key=True, verbose_name=u'ID(paymentId)')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'レコード作成時間')
    uid = models.PositiveIntegerField(verbose_name=u'ユーザID')
    iid = models.PositiveIntegerField(verbose_name=u'商品ID')
    inum = models.PositiveSmallIntegerField(verbose_name=u'購入数')
    price = models.PositiveIntegerField(verbose_name=u'値段')
    state = models.PositiveSmallIntegerField(verbose_name=u'課金状態', default=0)

class ShopPaymentEntry(PaymentEntry):
    """ショップの課金レコード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

class GachaPaymentEntry(PaymentEntry):
    """ガチャの課金レコード.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    continuity = models.PositiveSmallIntegerField(verbose_name=u'連続で回す回数', default=0)
