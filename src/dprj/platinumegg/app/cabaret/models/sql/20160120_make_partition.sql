CREATE INDEX userlogreprinttickettradeshop_uid_ctime on cabaret_userlogreprinttickettradeshop(`uid`, `ctime`);
ALTER TABLE `cabaret_userlogreprinttickettradeshop` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`, `ctime`);
ALTER TABLE `cabaret_userlogreprinttickettradeshop` PARTITION BY RANGE(TO_DAYS(`ctime`))(PARTITION `20151201` VALUES LESS THAN (TO_DAYS("2015-12-01 00:00:00")), PARTITION `20160101` VALUES LESS THAN (TO_DAYS("2016-01-01 00:00:00")), PARTITION `20160201` VALUES LESS THAN (TO_DAYS("2016-02-01 00:00:00")));
CREATE INDEX raideventhelpspecialbonusscore_id_ctime on cabaret_raideventhelpspecialbonusscore(`id`, `ctime`);
ALTER TABLE `cabaret_raideventhelpspecialbonusscore` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`, `ctime`);
ALTER TABLE `cabaret_raideventhelpspecialbonusscore` PARTITION BY RANGE(TO_DAYS(`ctime`))(PARTITION `20151201` VALUES LESS THAN (TO_DAYS("2015-12-01 00:00:00")), PARTITION `20160101` VALUES LESS THAN (TO_DAYS("2016-01-01 00:00:00")), PARTITION `20160201` VALUES LESS THAN (TO_DAYS("2016-02-01 00:00:00")));
CREATE INDEX raideventspecialbonusscorelog_id_ctime on cabaret_raideventspecialbonusscorelog(`id`, `ctime`);
ALTER TABLE `cabaret_raideventspecialbonusscorelog` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`, `ctime`);
ALTER TABLE `cabaret_raideventspecialbonusscorelog` PARTITION BY RANGE(TO_DAYS(`ctime`))(PARTITION `20151201` VALUES LESS THAN (TO_DAYS("2015-12-01 00:00:00")), PARTITION `20160101` VALUES LESS THAN (TO_DAYS("2016-01-01 00:00:00")), PARTITION `20160201` VALUES LESS THAN (TO_DAYS("2016-02-01 00:00:00")));
