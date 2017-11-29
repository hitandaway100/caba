# -*- coding: utf-8 -*-


class Media:
    
    @staticmethod
    def movie_m3u8(name):
        return u'%s.m3u8' % name
    
    @staticmethod
    def movie_flv(name):
        return u'%s/stream.flv' % name
    
    @staticmethod
    def movie_thumbnail(name):
        return u'%s/thumbnail.png' % name
    
    @staticmethod
    def movie_pc_thumbnail(name):
        return u'%s/pcthumbnail.png' % name
    
    @staticmethod
    def voice_aac(name):
        return u'%s/voice.m4a' % name
    
    @staticmethod
    def voice_ogg(name):
        return u'%s/voice.ogg' % name
    
    @staticmethod
    def movie_mp4(name):
        return u'%s.mp4' % name
    
