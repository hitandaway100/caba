CREATE INDEX userlogloginbonussugoroku_uid_ctime on cabaret_userlogloginbonussugoroku(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogloginbonussugoroku` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
ALTER TABLE `cabaret_userlogloginbonussugoroku` PARTITION BY RANGE(TO_DAYS(`ctime`))(PARTITION `20160101` VALUES LESS THAN (TO_DAYS('2016-01-01 00:00:00')));
