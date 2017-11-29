CREATE INDEX userlogpresentsend_uid_ctime on cabaret_userlogpresentsend(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogpresentsend` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
