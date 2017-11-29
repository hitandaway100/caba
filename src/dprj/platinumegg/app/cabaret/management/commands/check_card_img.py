# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import os
from defines import Defines

class Command(BaseCommand):
    """カード画像が全てあるかを確認する.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'check_card_img'
        print '================================'
        
        imgpath = os.path.join(os.path.dirname(__file__), '../../../../../../../static/img/sp')
        
        successlist_old, nglist_old = self.check('%s/card' % imgpath)
        successlist_l, nglist_l = self.check('%s/large/card' % imgpath)
        successlist_m, nglist_m = self.check('%s/medium/card' % imgpath)
        
        self.destResult('old', successlist_old, nglist_old)
        self.destResult('large', successlist_l, nglist_l)
        self.destResult('medium', successlist_m, nglist_m)
        
        print '---------------'
        print 'all done.'
    
    def destResult(self, name, successlist, nglist):
        print '---------------'
        print name
        print '---------------'
        print 'Success...%d' % len(successlist)
        for name, rare in successlist:
            if rare:
                print '%s...RARE' % name
            else:
                print '%s...NORMAL' % name
    
    def check(self, dirpath):
        FILENAMES = (
            'Card_thumb_52_52.png',
            'Card_thumb_60_75.png',
            'Card_thumb_110_138.png',
            'Card_thumb_320_400.png',
            'Card_thumb_320_314.png',
        )
        print '------------------------------'
        print 'check start %s' % dirpath
        
        successlist = []
        nglist = []
        for cardname in os.listdir(dirpath):
            imgpath_format = '%s/%s/%s' % (dirpath, cardname, '%s')
            flag_normal = True
            flag_rare = True
            print '-------------------'
            print '%s...start' % cardname
            for hklevel in xrange(1, Defines.HKLEVEL_MAX+1):
                for filename in FILENAMES:
                    p = 'H%d/%s' % (hklevel, filename)
                    if not os.path.exists(imgpath_format % p):
                        if hklevel == 1 or (flag_rare and 2 < hklevel):
                            flag_normal = False
                        flag_rare = False
                        print 'not found:%s' % p
                        nglist.append(imgpath_format % p)
            if flag_normal:
                successlist.append((cardname, flag_rare))
            
        print '------------------------------'
        print 'check end.'
        return successlist, nglist

