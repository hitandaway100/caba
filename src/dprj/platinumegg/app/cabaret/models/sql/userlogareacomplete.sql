CREATE INDEX userlogareacomplete_uid_ctime on cabaret_userlogareacomplete(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogareacomplete` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
