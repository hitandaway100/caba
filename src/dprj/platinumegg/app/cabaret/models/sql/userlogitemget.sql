CREATE INDEX userlogitemget_uid_ctime on cabaret_userlogitemget(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogitemget` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
