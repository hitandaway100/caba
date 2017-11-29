# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.lib.swf import SwfUtil
import os
import settings_sub

class Command(BaseCommand):
    """static/effect/pc以下のswfをバイナリに分割.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'swfunpack'
        print '================================'
        
        static_dir = settings_sub.STATIC_DOC_ROOT
        
        print '---------------'
        print 'search'
        print '---------------'
        def search(dirname):
            static_path = os.path.join(static_dir, dirname)
            
            def unpack(name):
                swf_path = os.path.join(static_path, name)
            
            for name in os.listdir(static_path):
                path = os.path.join(static_path, name)
                if os.path.isdir(path):
                    search(dirname + '/' + name)
                elif path.endswith('.swf'):
                    SwfUtil.unpack(path)
                    print path
        search('effect/pc')
        
        print '================================'
        print 'all done..'
