CREATE INDEX userlogcomposition_uid_ctime on cabaret_userlogcomposition(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogcomposition` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
