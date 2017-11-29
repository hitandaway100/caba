ALTER TABLE `cabaret_userlogcabaclubstore` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
ALTER TABLE `cabaret_userlogcabaclubstore` PARTITION BY RANGE(TO_DAYS(`ctime`))(PARTITION `20160201` VALUES LESS THAN (TO_DAYS('2016-02-01 00:00:00')));
