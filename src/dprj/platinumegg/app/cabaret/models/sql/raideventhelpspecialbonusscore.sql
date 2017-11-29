CREATE INDEX raideventhelpspecialbonusscore on cabaret_raideventhelpspecialbonusscore(`id`, `ctime`);
ALTER TABLE `cabaret_raideventhelpspecialbonusscore` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`, `ctime`);
ALTER TABLE `cabaret_raideventhelpspecialbonusscore`
      PARTITION BY RANGE(TO_DAYS(`ctime`))(
                PARTITION `20151201` VALUES LESS THAN (TO_DAYS("2015-12-01 00:00:00")),
                PARTITION `20160101` VALUES LESS THAN (TO_DAYS("2016-01-01 00:00:00"))
      );
