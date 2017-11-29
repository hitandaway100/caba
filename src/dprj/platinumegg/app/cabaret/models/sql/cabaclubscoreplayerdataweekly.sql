ALTER TABLE `cabaret_cabaclubscoreplayerdataweekly` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`week`);
ALTER TABLE `cabaret_cabaclubscoreplayerdataweekly` PARTITION BY RANGE(`week`)(PARTITION `20160101` VALUES LESS THAN (201601));
