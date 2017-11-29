# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import os
import settings_sub
import shutil

class Command(BaseCommand):
    """static以下の画像だけを集めてzip作成.
    """
    def handle(self, *args, **options):
        
        def mkdir(path):
            arr = path.split('/')
            for i in xrange(len(arr)):
                idx = i + 1
                p = '/'.join(arr[:idx])
                if p and not os.path.exists(p):
                    os.mkdir(p)
        
        print '================================'
        print 'copy_img'
        print '================================'
        
        static_dir = settings_sub.STATIC_DOC_ROOT
        
        if 0 < len(args):
            output_dir = args[0]
        else:
            output_dir = os.path.join(settings_sub.TMP_DOC_ROOT, 'images')
        
        if not os.path.exists(output_dir):
            mkdir(output_dir)
        elif os.path.isdir(output_dir):
            pass
        else:
            print 'not directory.path=%s' % output_dir
            return
        
        print '---------------'
        print 'search'
        print '---------------'
        def search(dirname):
            static_path = os.path.join(static_dir, dirname)
            output_path = os.path.join(output_dir, dirname)
            
            def cp(name):
                if not os.path.exists(output_path):
                    mkdir(output_path)
                shutil.copyfile(os.path.join(static_path, name), os.path.join(output_path, name))
            
            for name in os.listdir(static_path):
                path = os.path.join(static_path, name)
                if os.path.isdir(path):
                    search(dirname + '/' + name)
                elif os.path.splitext(name)[1] in ('.png', '.jpg', '.gif'):
                    cp(name)
                    print path
        search('img/sp')
        search('effect/sp')
        
        print '================================'
        print 'output directory=%s' % output_dir
        print 'all done..'
