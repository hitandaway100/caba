CREATE INDEX userlogpresentreceive_uid_ctime on cabaret_userlogpresentreceive(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogpresentreceive` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
