CREATE INDEX userlogcomeback_uid_ctime on cabaret_userlogcomeback(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogcomeback` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
