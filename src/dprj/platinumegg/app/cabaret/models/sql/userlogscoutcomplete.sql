CREATE INDEX userlogscoutcomplete_uid_ctime on cabaret_userlogscoutcomplete(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogscoutcomplete` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
