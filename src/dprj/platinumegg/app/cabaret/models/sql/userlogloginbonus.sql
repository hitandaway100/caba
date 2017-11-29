CREATE INDEX userlogloginbonus_uid_ctime on cabaret_userlogloginbonus(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogloginbonus` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
