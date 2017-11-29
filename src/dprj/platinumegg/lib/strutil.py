# -*- coding: utf-8 -*-
import unicodedata
import string

class StrUtil:
    @staticmethod
    def replaceText(text, value_list):
        dest = text
        for key in value_list.keys():
            dest = dest.replace('#{' + key + '}', value_list[key])
        return dest
    @staticmethod
    def getSubstringByte(text, byteI, byteJ):
        strI = 0
        strJ = 0
        byteLen = 0
        
        wide_chars = u"WFA"
        
        try:
            charI = 0
            while byteLen < byteI:
                c = text[charI]
                eaw = unicodedata.east_asian_width(c)
                if wide_chars.find(eaw) > -1:
                    byteLen += 2
                else:
                    byteLen += 1
                strI = charI
                charI += 1
        except IndexError:
            # 開始位置が範囲外.
            return ''
        
        try:
            charI = strI
            while byteLen <= byteJ:
                c = text[charI]
                eaw = unicodedata.east_asian_width(c)
                if wide_chars.find(eaw) > -1:
                    byteLen += 2
                else:
                    byteLen += 1
                strJ = charI
                charI += 1
        except IndexError:
            # 終了位置が範囲外.
            return text[strI:]
        
#        strI = 0
#        strJ = 0
#        byteLen = 0
#        charI = 0
#        while byteLen < byteI:
#            if ord(text[charI]) < 0x100:
#                byteLen += 1
#            else:
#                byteLen += 2
#            strI = charI
#            charI += 1
#        charI = strI
#        while byteLen <= byteJ:
#            if ord(text[charI]) < 0x100:
#                byteLen += 1
#            else:
#                byteLen += 2
#            strJ = charI
#            charI += 1
        return text[strI : strJ]
    @staticmethod
    def getByteLength(text):
        """
            半角での文字数取得.
        """
        return StrUtil.width_kana(text)
#        dest = 0
#        for s_i in range(len(text)):
#            if ord(text[s_i]) < 0x100:
#                dest += 1
#            else:
#                dest += 2
#        return dest
    @staticmethod
    def width_kana(text):
        length = len(text)      # 全文字数.
        zenkaku = StrUtil.count_zen(text)        # 全角文字数.
        hankaku = length - zenkaku     # 半角文字数.
        return zenkaku * 2 + hankaku
    @staticmethod
    def count_zen(text):
        n = 0
        wide_chars = u"WFA"
        for c in text:
            eaw = unicodedata.east_asian_width(c)
            if wide_chars.find(eaw) > -1:
                n += 1
        return n
    
    @staticmethod
    def trimText(text, byteLen, foot):
        #dbg.addLog((text + " len:" + str(StrUtil.getByteLength(text))).encode('utf-8'))
        if StrUtil.getByteLength(text) <= byteLen:
            return text
        else:
            return StrUtil.getSubstringByte(text, 0, byteLen - StrUtil.getByteLength(foot)) + foot
    
    @staticmethod
    def lrstrip(text):
        # 空白から始まっていた場合は取り除く
        s = text
        i = 0
        t = []
        while i < len(s):
            tmp = s[i]
            tmp = string.lstrip(string.lstrip(tmp, u'　'))
            tmp = string.rstrip(string.rstrip(tmp, u'　'))
            t.append(tmp)
            
            i = i + 1
        ret = string.join(t, u'')
        return ret
        
    # textがunicode型だったらstr型へ変換, str型の時はそのままを返す.
    # str 型に変換. すでに str形の場合はなにもしない.
    # @param text 変換したい文字列(unicode型)
    # @param dest_enc 変換先のエンコードタイプ.
    # @param src_enc 変換元のエンコードタイプ.
    @staticmethod
    def to_s(src, dest_enc = 'utf-8', src_enc= 'utf-8'):
        if src_enc == 'utf-8' and dest_enc == 'shift-jis':
            if type(src) is str:
                text_u = src
                text_u = StrUtil.to_u(text_u, src_enc)
                
#                text_u = text_u.replace(u'\xad', u'?')
#                text_u = text_u.replace(u'\uff5e', u'\u301c')
#                text_u = text_u.replace(u'\u2661', u'?') # ハートマーク.
#                text_u = text_u.replace(u'\u2666', u'◆')
                
                # return text_u.encode(dest_enc)
                return text_u.encode('cp932', 'ignore')
#                text_u = StrUtil.to_u(src, src_enc)
#                return text_u.encode(dest_enc)
            return src.encode(dest_enc, 'ignore')
        else:
            if type(src) is str:
                text_u = StrUtil.to_u(src, src_enc)
                return text_u.encode(dest_enc, 'ignore')
            return src.encode(dest_enc, 'ignore')
    ENCODES = ['utf-8', 'mbcs', 'shift-jis', 'euc-jp', 'iso2022-jp', ]
    
    # unicode 型に変換. すでに unicode形の場合はなにもしない.
    # str 型に変換. すでに str形の場合はなにもしない.
    # @param text 変換したい文字列(unicode型)
    # @param enc 変換元のエンコードタイプ.
    @staticmethod
    def to_u(text, src_enc = 'utf-8'):
        if type(text) is unicode:
            # dbg.addLog('to_u:(not enc)' + text)
            return text
        enc_text = unicode(text, src_enc, 'ignore')
        return enc_text
    
    @staticmethod
    def guess_charset(data):
        """文字コードを判定.
        """
        f = lambda d, enc: d.decode(enc) and enc
        codecs = ['shift_jis','utf-8','euc_jp','cp932',
              'euc_jis_2004','euc_jisx0213','iso2022_jp','iso2022_jp_1',
              'iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext',
              'shift_jis_2004','shift_jisx0213','utf_16','utf_16_be',
              'utf_16_le','utf_7','utf_8_sig'];
        for codec in codecs:
            try: return f(data, codec);
            except: continue;
        return None
    
    @staticmethod
    def toCamelCase(text):
        # キャメルケースに変換.
        up_flg = True
        ret = text.lower()
        UP_KEY = '_'
        for i in xrange(len(text)):
            s = text[i]
            if up_flg:
                ret = ret[0:i] + s.upper() + ret[i+1:]
                up_flg = False
            if s == UP_KEY:
                up_flg = True
        return ret.replace(UP_KEY, '')
