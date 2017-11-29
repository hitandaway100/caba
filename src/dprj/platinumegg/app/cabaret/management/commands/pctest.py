# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import os
import settings_sub

class Command(BaseCommand):
    """PC版テスト用.
    djangoの環境内で処理を行いたかったので.
    >> python manage.py pctest echo
    
    ●API指定されていなければ全部実行.
    ●ディレクトリになっていたらその中全部実行.
        -> 複数パターン確認するため.
    """
    MODULE_BASE = 'platinumegg.pctest'
    
    def putResult(self, result, taskname):
        if result:
            self.__success.append(taskname)
        else:
            self.__errors.append(taskname)
    
    def handle(self, *args, **options):
        
        if not settings_sub.IS_LOCAL:
            print 'This command is local only.'
            return
        
        msg = 'Please input test name.\n'
        msg += 'ex)target loc="test/pc/battleEnter/win", test name="battleEnter.win"\n'
        msg += 'test name:'
        resp = raw_input(msg)
        
        API = None
        API2 = None
        if resp != 'all':
            testnames = resp.split('.')
            
            try:
                API = testnames[0] or None
                if API[-1] == ';':
                    # どうでもいいんだけど勢いで最後に「;」つける事がよくあるので.
                    API = API[0:-1]
            except IndexError:
                API = None
            if 1 < len(testnames):
                API2 = testnames[1]
        
        self.__success = []
        self.__errors = []
        
        print '================================'
        if API is None:
            # API指定されてなかったら全部実行.
            print 'run all.'
            print '================================'
            # まずはパッケージを検索.
#            pack = __import__(name, globals={}, locals={}, fromlist=)
            
            module = Command.__myimoport(Command.MODULE_BASE)
#            for k,v in module.__dict__.items():
#                print '%s:%s' % (k,v)
            files = os.listdir(module.__path__[0])
            
            IGNORES = ['__init__','base']
            for filename in files:
                if filename[-3:] == '.py':
                    api = filename[0:-3]
                    if api not in IGNORES:
                        print 'modname=%s.%s' % (Command.MODULE_BASE, api)
                        module = Command.__myimoport('%s.%s' % (Command.MODULE_BASE, api))
                        result = module.ApiTest.run(api)
                        self.putResult(result, api)
                elif filename.find('.') == -1:
                    # パッケージらしきもの.
                    if filename not in IGNORES:
                        self.__run_package(filename, API2)
            
        else:
            module = Command.__myimoport(Command.MODULE_BASE)
            files = os.listdir(module.__path__[0])
            if API in files:
                # たぶんパッケージ.
                self.__run_package(API, API2)
            else:
                module = Command.__myimoport('%s.%s' % (Command.MODULE_BASE, API))
                result = module.ApiTest.run(API)
                self.putResult(result, API)
        
        print '================================'
        print 'all end.'
        print 'success:%d' % len(self.__success)
        print 'error:%d' % len(self.__errors)
        for api in self.__errors:
            print '\t%s' % api
    
    def __run_package(self, package_name, api):
        # パッケージらしきものを走らせる.
        IGNORES = ['__init__']
        module_base = '%s.%s' % (Command.MODULE_BASE, package_name)
        
        if api is not None:
            # 実行するものが指定されていたらそれ実行.
            print 'module:%s' % (api)
            print '---------------'
            module = Command.__myimoport('%s.%s' % (module_base, api))
            result = module.ApiTest.run(package_name)
            self.putResult(result, '%s.%s' % (package_name, api))
            return
        
        module = Command.__myimoport(module_base)
        filenames2 = os.listdir(module.__path__[0])
        for filename2 in filenames2:
            if filename2[-3:] == '.py':
                module_name = filename2[0:-3]
                if module_name not in IGNORES:
                    print 'module:%s' % (module_name)
                    print '---------------'
                    module = Command.__myimoport('%s.%s' % (module_base, module_name))
                    result = module.ApiTest.run(package_name)
                    self.putResult(result, '%s.%s' % (package_name, module_name))
        
    @staticmethod
    def __myimoport(name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod
    