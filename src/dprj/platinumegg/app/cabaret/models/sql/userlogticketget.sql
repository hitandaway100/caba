CREATE INDEX userlogticketget_uid_ctime on cabaret_userlogticketget(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogticketget` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
