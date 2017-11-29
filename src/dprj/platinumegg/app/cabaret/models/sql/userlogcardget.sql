CREATE INDEX userlogcardget_uid_ctime on cabaret_userlogcardget(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogcardget` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
