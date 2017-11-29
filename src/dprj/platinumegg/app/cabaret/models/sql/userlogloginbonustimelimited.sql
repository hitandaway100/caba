CREATE INDEX userlogloginbonustimelimited_uid_ctime on cabaret_userlogloginbonustimelimited(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogloginbonustimelimited` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
