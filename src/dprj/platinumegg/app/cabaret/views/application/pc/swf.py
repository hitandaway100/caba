# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
import os
import settings_sub
import json
from struct import pack

class Handler(AppHandler):
    """分割されているSWFバイナリを結合して返す
    負荷高そう…高いよなぁ…
    """
    
    def checkUser(self):
        pass
    
    def check_process_pre(self):
        return True
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    @staticmethod
    def chunk(obj_id, raw):
        """ヘッダを付加してチャンクデータを返す
        """
        tagid = 21 #DefineBitsJPEG2
        head = pack("<H", ((tagid << 6) | 0x3F)) + pack("<I", len(raw) + 2)
        objid = pack("<H", obj_id)
    
        return (head + objid + raw)
    
    def process(self):
        args = self.getUrlArgs('/swf/')
        length = args.length()
        name = 'pc'
        for i in xrange(length):
            name = os.path.join(name, args.get(i, None))
        
        path = os.path.join(settings_sub.STATIC_DOC_ROOT, 'effect')
        path = os.path.join(path, name)
        
        # jsonファイルを開く
        name = path[:-4]
        f = open("%s.json" % name, "r")
        data = json.load(f)
        f.close()
        
        num = data["num"]
        
        # 置き換える画像名を取得する
        replace_images = {}
        replace_paths = {}
        for k in data:
            url = self.request.get(k)
            if url:
                file_no = data[k]["file_no"]
                replace_images[file_no] = k
                replace_paths[file_no] = url.replace(settings_sub.STATIC_URL_ROOT, settings_sub.STATIC_DOC_ROOT + '/')
        
        # header
        f = open("%s_header.bin" % name, "rb")
        buf = f.read()
        f.close()
        
        # etc
        for i in xrange(num):
            if i in replace_images:
                # 置き換える
                f = open(replace_paths[i], "rb")
                raw = f.read()
                f.close()
                buf = buf + Handler.chunk(data[replace_images[i]]["obj_id"],raw)
            else:
                n = "%s_%d.bin" % (name, i)
                f = open(n, "rb")
                buf = buf + f.read()
                f.close()
        
        # ファイルサイズ書き換え
        buf = buf[:4] + pack("<I", len(buf)) + buf[8:]
        
        self.response.set_header('Content-Type', 'application/x-shockwave-flash')
        self.response.set_status(200)
        self.response.send(buf)
    
    
def main(request):
    return Handler.run(request)
