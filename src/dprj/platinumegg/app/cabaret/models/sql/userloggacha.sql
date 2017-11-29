CREATE INDEX userloggacha_uid_ctime on cabaret_userloggacha(`uid`,`ctime`);
ALTER TABLE `cabaret_userloggacha` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
