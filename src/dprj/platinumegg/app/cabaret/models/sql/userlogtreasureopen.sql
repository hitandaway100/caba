CREATE INDEX userlogtreasureopen_uid_ctime on cabaret_userlogtreasureopen(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogtreasureopen` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
