CREATE INDEX userlogcardstock_uid_ctime on cabaret_userlogcardstock(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogcardstock` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
