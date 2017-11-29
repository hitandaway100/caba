CREATE INDEX userlogcardsell_uid_ctime on cabaret_userlogcardsell(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogcardsell` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
