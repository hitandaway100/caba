# -*- coding: utf-8 -*-
import os
import settings_sub
import sys
from struct import pack, unpack
from StringIO import StringIO

class SwfTagDefines:
    End=0
    ShowFrame=1
    DefineShape=2
    PlaceObject=4
    RemoveObject=5
    DefineBits=6
    DefineButton=7
    JPEGTables=8
    SetBackgroundColor=9
    DefineFont=10
    DefineText=11
    DoAction=12
    DefineFontInfo=13
    DefineSound=14
    StartSound=15
    DefineButtonSound=17
    SoundStreamHead=18
    SoundStreamBlock=19
    DefineBitsLossLess=20
    DefineBitsJPEG2=21
    DefineShape2=22
    DefineButtonCxform=23
    Protect=24
    PlaceObject2=26
    RemoveObject2=28
    DefineShape3=32
    DefineText2=33
    DefineButton2=34
    DefineBitsJPEG3=35
    DefineBitsLossLess2=36
    DefineEditText=37
    DefineSprite=39
    FrameLabel=43
    SoundStreamHead2=45
    DefineMorphShape=46
    DefineFont2=48
    ExportAssets=56
    ImportAssets=57
    EnableDebugger=58
    DoInitAction=59
    DefineVideoStream=60
    VideoFrame=61
    DefineFontInfo2=62
    EnableDebugger2=64
    ScriptLimits=65
    SetTabIndex=66
    FileAttributes=69
    PlaceObject3=70
    ImportAssets2=71
    DefineFontAlignZones=73
    CSMTextSettings=74
    DefineFont3=75
    SymbolClass=76
    Metadata=77
    DefineScalingGrid=78
    DoABC=82
    DefineShape4=83
    DefineMorphShape2=84
    DefineSceneAndFrameLabelData=86
    DefineBinaryData=87
    DefineFontName=88
    StartSound2=89
    DefineBitsJPEG4=90
    DefineFont4=91
    
    NOT_NECESSITY_TAGS = [
        Metadata,
    ]


class SwfTagHead:
    """チャンクヘッダ
    """
    __head = None#type, length などが入ってるバイナリ.長さが2byteの場合と6byteの場合がある.
    __type = 0
    __length = 0
    
    def __init__(self, file):
        """bytestream(fileからheadを作成.
        """
        byte12 = file.read(2)
        if len(byte12) < 2:
            return #読めません. 
        head = unpack("<H", byte12)[0]
        self.__type = (head & 0xFFC0) >> 6  #0b1111111111000000
        self.__length = head & 0x3f #0b111111
        if TAG_TYPE.has_key(self.__type):
            head_class_name = TAG_TYPE[self.__type].__name__
        else:
            head_class_name = "????"
        
        self.__head = byte12
        
        if 0x3f == self.__length:
            byte3456 = file.read(4)
            self.__length = unpack("<I", byte3456)[0]
            self.__head += byte3456
    
    def length(self):
        """length"""
        return self.__length
    
    def type(self):
        """type"""
        return self.__type
    
    def head_length(self):
        if None == self.__head:
            return 0
        return len(self.__head)
    
    def data(self):
        return self.__head


class SwfTag(object):
    """チャンクフォーマットのそれぞれのタグ.
    タイプ、長さ、データ、と入る
    短い場合(0x3f未満) __type:10bits, __length=6bits,
    長い場合(0x3f以上) __type:10bits, (6bitsダミー), __length:4bytes, 
    となっているらしい
    
    ..どうしよう..
    file読んでく形だから,,length決まって、そっからdata分読んで、ってループになるはず.
    """
    HEAD_SIZE = 6
    DATA_OFFSET = 4
    
    __head = u''#TagHead
    __data = u'' #__lengthの長さ分だけbyteで入ってる
    __offset = 0
    def __init__(self, head, file, offset,id):
        self.__head = head
        self.__data = file.read(head.length())
        self.__offset = offset
    
    def type(self):
        return self.__head.type()
    
    def length(self):
        """タグ全体の長さ"""
        return self.__head.length() + self.__head.head_length() 
    
    def offset(self):
        """
        ここはオフセットを返せるようにしておかないと行けない
        """
        return self.__offset
    
    def data(self):
        return self.__data
    
    def bytes(self):
        return self.__head.data() + self.__data


class SwfTagEnd(SwfTag):
    #dataはこいつは実際には無いけど...
    pass


class SwfTagObject(SwfTag):
    """基本的に画像,shape, spriteとかはこの形式を踏襲している.
    """
    __object_id = 0
    
    def __init__(self, head, file, offset, id):
        super(SwfTagObject, self).__init__(head, file, offset, id)
        self.__object_id =unpack("<H", self.data()[0:2])[0]
    
    def object_id(self):
        return self.__object_id


class SwfTagExportAssets(SwfTag):
    """ Exportのタグ.データ取得用に使う.実機で入ってる必要は無い
    """
    __object_id = 0
    __count = 0
    __name = ""
    
    def __init__(self, head, file, offset, id):
        super(SwfTagExportAssets, self).__init__(head, file, offset, id)
        self.__count =unpack("<H", self.data()[0:2])[0]
        self.__object_id =unpack("<H", self.data()[2:4])[0]
        self.__name= self.data()[4:-1]
    
    def name(self):
        return self.__name
    
    def object_id(self):
        return self.__object_id



TAG_TYPE={
    0:SwfTagEnd,#End
    6:SwfTagObject,#DefineBits
    20:SwfTagObject,#DefineBitsLossless
    21:SwfTagObject,#DefineBitsJPEG2
    35:SwfTagObject,#DefineBitsJPEG3
    36:SwfTagObject,#DefineBitsLossless2
    56:SwfTagExportAssets,#ExportAssets
    90:SwfTagObject,#DefineBitsJPEG4
}


class SwfHeader:
    """swfのヘッダ.
    """
    
    __bytes = None  # 生データ
    __filesize = 0  # ファイル全体のサイズ
    __header_length = 0 # ヘッダ長
    
    def __init__(self, stream):
        """bytestream(fileからheadを作成.
        """
        
        byte1234 = stream.read(4)
        byte5678 = stream.read(4)
        
        # header_movieは可変長
        byte9 = stream.read(1)
        bits_size = (unpack("<B", byte9)[0] & 0xF8) >> 3     #0b11111000
        byte_length = ((bits_size * 4) - 3 + 7) >> 3    # (x_min, x_max, y_min, y_max) * bits_size | byte align
        byte_length = byte_length + 4                   # frame_rate, frame_rate_count
        byte9plus = byte9 + stream.read(byte_length)
        
        self.__filesize =unpack("<I", byte5678)[0]
        self.__bytes = byte1234 + byte5678 + byte9plus
        if "F" != byte1234[0]:
            if "CWS" == byte1234[0:2]:
                raise Exception("illegal. CWS?") # なんかこいつCWSですよ.(パブリッシュ時の圧縮をオフにしてください.
            else:
                raise Exception("illegal. " + byte1234)
        
        print "filesize:%s" % (self.__filesize) # こいつは確かにファイル全体のサイズが入ってる
        self.__header_length = 4 + 4 + 1 + byte_length
    
    def length(self):
        return self.__header_length
    
    def bytes(self):
        return self.__bytes
    
    def swfsize(self):
        return self.__filesize
    
    def set_swfsize(self, size):
        """swfSizeの変更.
        """
        packed_size = pack("<I", size)
        self.__bytes = self.__bytes[:4] + packed_size + self.__bytes[8:]
        self.__filesize = size
    
    
class SwfUtil:
    """SWF関係.
    """
    
    @staticmethod
    def unpack(filename):
        """swfファイルを分割する.
        """
        if(not filename.endswith('.swf')):
            raise Exception("not swf file.%s" % filename)
        
        # ファイルを開いてヘッダを解析してみる
        file = open(filename, "rb")
        try:
            header = SwfHeader(file)
        except:
            raise Exception("header maybe cws.%s" % filename)
        
        # 無事解析出来たので処理を続行
        offset = header.length()
        swfsize = header.swfsize()
        
        tags = []
        exports = {}
        images = {}
        count = 0
        
        # タグ別の関数テーブル
        table = {
            SwfTagDefines.ExportAssets         : SwfUtil.__proc_asset,
            SwfTagDefines.DefineBits           : SwfUtil.__proc_resources,
            SwfTagDefines.DefineBitsLossLess   : SwfUtil.__proc_resources,
            SwfTagDefines.DefineBitsLossLess2  : SwfUtil.__proc_resources,
            SwfTagDefines.DefineBitsJPEG2      : SwfUtil.__proc_resources,
            SwfTagDefines.DefineBitsJPEG3      : SwfUtil.__proc_resources,
            SwfTagDefines.DefineBitsJPEG4      : SwfUtil.__proc_resources,
        }
        
        while True: # 無限ループに陥らないように注意
            # チャンクヘッダ取得
            head = SwfTagHead(file)
            if 0 == head.head_length():
                break
            
            # タグタイプで処理クラスを分ける
            h_type = head.type()
            if TAG_TYPE.has_key(h_type):
                cls = TAG_TYPE[h_type]
            else:
                cls = SwfTag
            
            #print "tag: # %d:type %d: %s" % (count, h_type, cls.__name__)
            tag = cls(head, file, offset, count)
            tags.append(tag)
            
            if not h_type in SwfTagDefines.NOT_NECESSITY_TAGS:
                # 各タグ用の関数を呼び出す
                proc = table.get(h_type)
                if proc != None:
                    proc(tag, exports, images, count)
            else:
                swfsize -= tag.length()
            
            count += 1
            offset += tag.length()
        
        # ヘッダのバイナリをファイルへ出力
        name = filename[:-4]
        f = open("%s_header.bin" % name, "wb")
        f.write(header.bytes())
        f.close()
        
        # バイナリを書き出す
        buf = None
        buf_count = 0
        file_no = {}
        for i in xrange(count):
            if i in images:
                # 画像系
                if buf:
                    f = open("%s_%d.bin" % (name, buf_count), "wb")
                    f.write(buf)
                    f.close()
                    buf = None
                    buf_count += 1
                
                file_no[i] = buf_count
                f = open("%s_%d.bin" % (name, buf_count), "wb")
                f.write(tags[i].bytes())
                f.close()
                buf_count += 1
            else:
                # その他
                if buf:
                    buf = buf + tags[i].bytes()
                else:
                    buf = tags[i].bytes()
        
        # 残りを書き出す
        if buf:
            f = open("%s_%d.bin" % (name, buf_count), "wb")
            f.write(buf)
            f.close()
            buf_count += 1
        
        # 画像ファイルの在処をjsonで吐き出す
        f = open("%s.json" % name, "w")
        f.write('{\n\t"num":%d' % buf_count)
        for i in images:
            f.write(',\n\t"%s": { "file_no":%d, "obj_id":%d }' % (exports[images[i]], file_no[i], images[i]))
        f.write('\n}')
        f.close()
    
    @staticmethod
    def __proc_asset(tag, exports, images, count):
        """Assetタグの処理.
        ここはtagの名前をタグ番号に対応させるテーブルへ突っ込む
        """
        #print "export %s:%d"%(tag.name(), tag.object_id())
        exports[tag.object_id()] = tag.name()
        
        return SwfUtil.__make_proc_result(exports, images, True)
    
    @staticmethod
    def __proc_resources(tag, exports, images, count):
        """リソース系タグの処理.
        """
        #print "object id %d" % tag.object_id()
        images[count] = tag.object_id()
        
        return SwfUtil.__make_proc_result(exports, images, False)
    
    @staticmethod
    def __make_proc_result(exports, images, is_asset):
        """各タグの処理の結果作成.
        """
        return {
            'exports':exports,
            'images':images,
            'is_asset':is_asset,
        }
