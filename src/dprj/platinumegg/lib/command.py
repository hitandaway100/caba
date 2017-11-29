# -*- coding: utf-8 -*-
import commands
import settings_sub
import pexpect

class CommandUtil():
    """コマンド実行.
    """
    
    @staticmethod
    def makeCommandString(cmd, args, workdir=None):
        commandlist = []
        if workdir:
            commandlist.append('cd "%s"' % workdir)
        commandlist.append('%s %s' % (cmd, ' '.join(args)))
        return ';'.join(commandlist)
    
    @staticmethod
    def execute(commandlist, log=False):
        command = ';'.join(commandlist)
        status, consolelog = commands.getstatusoutput(command)
        
        if int(status) == 0 and not log:
            return None
        else:
            return consolelog
    
    @staticmethod
    def expect(command, expect_args):
        """expect
        """
        obj = pexpect.spawn(command)
        
        def _expect(_expect_args):
            keys = _expect_args.keys()[:]
            args = _expect_args.values()
            
            keys.append(pexpect.EOF)
            
            idx = obj.expect(keys)
            if idx < len(args):
                v = args[idx]
                if isinstance(v, tuple):
                    obj.sendline(v[0])
                    _expect(v[1])
                else:
                    obj.sendline(v)
                    obj.expect(pexpect.EOF)
        _expect(expect_args)
    
