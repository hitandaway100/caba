# -*- coding: utf-8 -*-
import os
from platinumegg.lib.command import CommandUtil
import settings_sub

class MovieUtil():
    """動画関係.
    """
    
    @staticmethod
    def ffmpeg(cmd_args, workdir=None):
        command = CommandUtil.makeCommandString('ffmpeg', cmd_args, workdir)
#        command = CommandUtil.makeCommandString('/usr/local/bin/ffmpeg', cmd_args, workdir)
        #command = CommandUtil.makeCommandString('/opt/local/bin/ffmpeg', cmd_args, workdir)
        consolelog = CommandUtil.execute([command])
        return consolelog
    
    @staticmethod
    def to_mpeg2ts(inputname, outputname=None, vcodec='copy', acodec='copy', workdir=None, *args, **kwargs):
        """動画をmpeg2-tsに変換.
        example) prj/CabaretQuest で作業.
                ffmpeg -i stream/test.mp4 -s 320x180 -vcodec libx264 -acodec copy -aspect 16:9 -vbsf h264_mp4toannexb stream/test.ts
                    ->to_mpeg2ts('stream/test.mp4', 'stream/test.ts', 'libx264', 'copy', 'prj/CabaretQuest', '-s', '320x180', '-aspect' '16:9')
        """
        cmd_args = [
            '-i', inputname,
            '-vcodec', vcodec,
            '-acodec', acodec,
            '-y'
        ]
        
        if args:
            cmd_args.extend(args)
        
        for tpl in kwargs.items():
            cmd_args.extend(tpl)
        
        cmd_args.extend(['-vbsf', 'h264_mp4toannexb'])
        if outputname:
            cmd_args.append(outputname)
        
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def segment(inputname, segment_list_name, ts_outputformat, segment_format='mpegts', segment_list_type='m3u8', segment_time='10', workdir=None, *args, **kwargs):
        """動画をHLS用に分割.
        ts->m3u8しか動作確認してませんよ.
        """
        cmd_args = [
            '-i', inputname,
            '-map', '0',
            '-f', 'segment',
            '-segment_format', segment_format,
            '-segment_list_type', segment_list_type,
            '-segment_time', segment_time,
            '-y'
        ]
        if args:
            cmd_args.extend(args)
        
        for tpl in kwargs.items():
            cmd_args.extend(tpl)
        
        if inputname[-4:] == '.mp4':
            cmd_args.extend(['-vbsf', 'h264_mp4toannexb', '-flags', '+global_header'])
        
        cmd_args.extend(['-segment_list', segment_list_name])
        cmd_args.append(ts_outputformat)
        
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def make_capture_image(inputname, outputname, start_second=0, frames=1, size=None, workdir=None):
        """動画のキャプチャを作成.
        ffmpeg -ss 1 -vframes 1 -i in.flv -f image2 out.png
        """
        cmd_args = [
            '-y',
            '-i', inputname,
            '-f', 'image2',
            '-ss', str(start_second),
            '-vframes', str(frames),
        ]
        if size:
            cmd_args.extend(['-s', size])
        cmd_args.append(outputname)
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def to_flv(inputname, outputname=None, vcodec='copy', acodec='copy', workdir=None, *args, **kwargs):
        """flvに変換.
        """
        cmd_args = [
            '-y',
            '-i', inputname,
            '-vcodec', vcodec,
            '-acodec', acodec,
            '-f', 'flv'
        ]
        if args:
            cmd_args.extend(args)
        
        for tpl in kwargs.items():
            cmd_args.extend(tpl)
        
        if outputname:
            cmd_args.append(outputname)
        
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def to_mp4(inputname, outputname=None, vcodec='copy', acodec='copy', workdir=None, *args, **kwargs):
        """mp4に変換.
        """
        cmd_args = [
            '-y',
            '-i', inputname,
            '-vcodec', vcodec,
            '-acodec', acodec,
            '-f', 'mp4'
        ]
        if args:
            cmd_args.extend(args)
        
        for tpl in kwargs.items():
            cmd_args.extend(tpl)
        
        if outputname:
            cmd_args.append(outputname)
        
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def to_swf(inputname, outputname=None, acodec='copy', workdir=None, *args, **kwargs):
        """swfに変換.
        """
        cmd_args = [
            '-y',
            '-i', inputname,
            '-acodec', acodec,
            '-f', 'swf'
        ]
        if args:
            cmd_args.extend(args)
        
        for tpl in kwargs.items():
            cmd_args.extend(tpl)
        
        if outputname:
            cmd_args.append(outputname)
        
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def to_aac(inputname, outputname=None, acodec='copy', workdir=None, *args, **kwargs):
        """aacに変換.
        """
        cmd_args = [
            '-y',
            '-i', inputname,
            '-vn',
            '-acodec', acodec,
            '-f', 'ipod'
        ]
        if args:
            cmd_args.extend(args)
        
        for tpl in kwargs.items():
            cmd_args.extend(tpl)
        
        if outputname:
            cmd_args.append(outputname)
        
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def to_ogg(inputname, outputname=None, acodec='copy', workdir=None, *args, **kwargs):
        """oggに変換.
        """
        cmd_args = [
            '-y',
            '-i', inputname,
            '-vn',
            '-acodec', acodec,
            '-f', 'ogg'
        ]
        if args:
            cmd_args.extend(args)
        
        for tpl in kwargs.items():
            cmd_args.extend(tpl)
        
        if outputname:
            cmd_args.append(outputname)
        
        return MovieUtil.ffmpeg(cmd_args, workdir)
    
    @staticmethod
    def crypt(hexkey, inputfile_format, outputfile_format, flag_delete_inputfile=True, workdir=None):
        """暗号化.
        """
        arr = []
        if workdir:
            arr.append('cd "%s"' % workdir)
            inputfilepath_format = '{workdir}/%s'.format(workdir=workdir)
        else:
            inputfilepath_format = '%s'
        
        arr.append('openssl aes-128-cbc -e -in {inputfile} -out {outputfile} -p -nosalt -iv {hexnumber} -K %s' % (hexkey))
        if flag_delete_inputfile:
            arr.append('rm -f {inputfile}')
        command_format = ';'.join(arr)
        
        for i in xrange(1000):
            inputfile = inputfile_format % i
            if not os.path.exists(inputfilepath_format % inputfile):
                break
            
            outputfile = outputfile_format % i
            command = command_format.format(inputfile=inputfile, outputfile=outputfile, hexnumber='%032x' % i)
            consolelog = CommandUtil.execute([command])
            if consolelog:
                return consolelog
        return None
    
    @staticmethod
    def distribute(name, weblist, password=None):
        """メディアサーバに一式配付する.
        """
        commandlist = []
        if password:
            for web in weblist:
                s = web.rstrip('\n').rstrip('\r')
                expect_args = {
                    'Are you sure you want to continue connecting.*' : ('yes', {'.assword.*' : password}),
                    '.assword.*' : password,
                }
                CommandUtil.expect(CommandUtil.makeCommandString('scp', ['-r', os.path.join(settings_sub.MEDIA_DOC_ROOT, name), 'root@%s:%s/' % (s, settings_sub.MEDIA_DOC_ROOT)]), expect_args)
                CommandUtil.expect(CommandUtil.makeCommandString('scp', [os.path.join(settings_sub.MEDIA_DOC_ROOT, '%s.m3u8' % name), 'root@%s:%s/' % (s, settings_sub.MEDIA_DOC_ROOT)]), expect_args)
        else:
            for web in weblist:
                s = web.rstrip('\n').rstrip('\r')
                commandlist.append(CommandUtil.makeCommandString('scp', ['-r', name, 'root@%s:%s/' % (s, settings_sub.MEDIA_DOC_ROOT)], workdir=settings_sub.MEDIA_DOC_ROOT))
                commandlist.append(CommandUtil.makeCommandString('scp', ['%s.m3u8' % name, 'root@%s:%s/' % (s, settings_sub.MEDIA_DOC_ROOT)], workdir=settings_sub.MEDIA_DOC_ROOT))
            for cmd in commandlist:
                errlog = CommandUtil.execute([cmd])
                if errlog:
                    return errlog
            return None
    
    @staticmethod
    def distribute_pc(name, weblist, password=None):
        """メディアサーバに一式配付する(PC).
        """
        # TODO:サムネイル画像だけ送りたい
        commandlist = []
        if password:
            for web in weblist:
                s = web.rstrip('\n').rstrip('\r')
                expect_args = {
                    'Are you sure you want to continue connecting.*' : ('yes', {'.assword.*' : password}),
                    '.assword.*' : password,
                }
                CommandUtil.expect(CommandUtil.makeCommandString('scp', ['-r', os.path.join(settings_sub.MEDIA_DOC_ROOT, name), 'root@%s:%s/' % (s, settings_sub.MEDIA_DOC_ROOT)]), expect_args)
        else:
            for web in weblist:
                s = web.rstrip('\n').rstrip('\r')
                commandlist.append(CommandUtil.makeCommandString('scp', ['-r', name, 'root@%s:%s/' % (s, settings_sub.MEDIA_DOC_ROOT)], workdir=settings_sub.MEDIA_DOC_ROOT))
            for cmd in commandlist:
                errlog = CommandUtil.execute([cmd])
                if errlog:
                    return errlog
            return None
    
    @staticmethod
    def distribute_wowza(name):
        """Wowzaサーバに一式配付する.
        """
        if settings_sub.IS_LOCAL:
            # ローカルの場合はsettings_sub.MEDIA_DOC_ROOTに配置済み.
            pass
        else:
            hosts = getattr(settings_sub, 'WOWZA_UPLOAD_HOST')
            if isinstance(hosts, (list, tuple)):
                hosts = list(hosts)
            elif isinstance(hosts, (str, unicode)) and hosts:
                hosts = [hosts]
            else:
                hosts = None
            password = settings_sub.SERVER_PASS
            expect_args = {
                'Are you sure you want to continue connecting.*' : ('yes', {'.assword.*' : password}),
                '.assword.*' : password,
            }
            for host in (hosts or []):
                CommandUtil.expect(CommandUtil.makeCommandString('scp', [os.path.join(settings_sub.MEDIA_DOC_ROOT, '%s.mp4' % name), 'root@%s:%s/' % (host, settings_sub.WOWZA_CONTENT_ROOT)]), expect_args)

