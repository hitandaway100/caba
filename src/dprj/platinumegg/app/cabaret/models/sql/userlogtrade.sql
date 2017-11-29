CREATE INDEX userlogtrade_uid_ctime on cabaret_userlogtrade(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogtrade` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
