# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
from platinumegg.lib.opensocial.util import OSAUtil
import os
import settings_sub

class Command(BaseCommand):
    """KPIの集計.
    """
    def handle(self, *args, **options):
        
        starttime = OSAUtil.get_now()
        
        print '================================'
        print 'aggregate_kpi'
        print '================================'
        
        REQUIRED_ARG_LENGTH = 1
        OPTIONAL_ARG_LENGTH = 2
        (
            ARGINDEX_TARGET,
        ) = range(REQUIRED_ARG_LENGTH)
        (
            ARGINDEX_DATE,
            ARGINDEX_OUTPUT_DIR,
        ) = range(REQUIRED_ARG_LENGTH, REQUIRED_ARG_LENGTH+OPTIONAL_ARG_LENGTH)
        
        if len(args) < REQUIRED_ARG_LENGTH:
            print 'Illegal Arguments...'
            print 'example) python manage.py aggregate_kpi playerlevel'
            return
        
        now = OSAUtil.get_now()
        
        targetname = args[ARGINDEX_TARGET]
        
        if ARGINDEX_DATE < len(args):
            tmp = args[ARGINDEX_DATE]
            try:
                targetdate = datetime.datetime.strptime(tmp, "%Y/%m/%d")
            except:
                print 'Illegal Arguments...DateTime format error..v=%s' % tmp
                print 'example) python manage.py aggregate_kpi playerlevel 2013/10/31'
                return
        else:
            if settings_sub.IS_LOCAL:
                targetdate = now
            else:
                targetdate = now - datetime.timedelta(days=1)
        
        output_dir = None
        if ARGINDEX_OUTPUT_DIR < len(args):
            output_dir = args[ARGINDEX_OUTPUT_DIR]
        output_dir = output_dir or settings_sub.KPI_ROOT
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        
        mod = getattr(__import__('platinumegg.app.cabaret.kpi.csv', globals(), locals(), [targetname], -1), targetname, None)
        if not mod:
            print 'Invalid targetname...targetname=%s' % targetname
            print 'example) python manage.py aggregate_kpi playerlevel'
            return
        
        ins = mod.Manager(targetdate, output_dir)
        ins.write()
        
        print '================================'
        print 'all end..'
        
        diff = OSAUtil.get_now() - starttime
        sec = diff.days * 86400 + diff.seconds
        print 'time %d.%06d' % (sec, diff.microseconds)
