CREATE INDEX userlogtreasureget_uid_ctime on cabaret_userlogtreasureget(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogtreasureget` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
