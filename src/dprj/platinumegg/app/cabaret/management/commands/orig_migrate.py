# coding: utf-8
import os
import glob

from django.db import connection
from django.db import connections
from django.core.management.base import BaseCommand

import settings
import settings_sub
from  platinumegg.app.cabaret.models import sql

class Command(BaseCommand):
    """マイグレーション用.
    django の 1.4 に既存のテーブルに対しての変更を検知して Alter Table を当ててくれるものが無いので.
    >> python manage.py orig_migrate

    このコマンドは, バージョン番号がファイルの先頭に付いている sql を実行します.
    バージョン番号の定義は models/sql/__init__.py に書いていますので,
    次のカラム変更を行ないたい日をバージョンに設定しておくと良いです.
    下記例のファイルの様に, どのモデルに対して何をするのか (add, delete, ... 等) を名前に付ける事を推奨.
    ex) dprj/platinumegg/app/cabaret/models/sql/20150914_add_column_gachamaster.sql
    """
    def handle(self, *args, **options):
        self.stdout.write('Change table ...\n')
        if os.path.isdir(sql.DIR):
            migrates = glob.glob(sql.DIR + sql.VERSION + '*.sql')
            if migrates:
                cursor = connections[settings.DB_DEFAULT].cursor()
                self.stdout.write(
                    '!!! Migrate Version: {}, MasterDB: {} !!!'.format(
                        sql.VERSION,
                        settings.DATABASES[cursor.db.alias]['HOST']
                    )
                )
                for migrate in migrates:
                    self.stdout.write('\033[0m# {}'.format(os.path.basename(migrate)))
                    with open(migrate, 'r') as sql_file:
                        success_count = 0
                        errors = []
                        for sql_line in sql_file.readlines():
                            try:
                                self.stdout.write('\033[0mexec: {}'.format(sql_line))
                                cursor.execute(sql_line)
                                success_count += 1
                                self.stdout.write('\033[32mexec OK.')
                            except Exception as errno:
                                errors.append('\033[31mExecError: {} \n'.format(errno))
                        self.stdout.write('Success {0}, Error : {1}.'.format(success_count, len(errors)))
                        for error in errors:
                            self.stdout.write(error)
            else:
                self.stdout.write('Not Change SQL ...\n')
