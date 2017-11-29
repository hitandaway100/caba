CREATE INDEX userlogitemuse_uid_ctime on cabaret_userlogitemuse(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogitemuse` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
