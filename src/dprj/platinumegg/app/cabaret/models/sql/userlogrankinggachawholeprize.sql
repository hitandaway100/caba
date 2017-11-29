CREATE INDEX userlogrankinggachawholeprize_uid_ctime on cabaret_userlogrankinggachawholeprize(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogrankinggachawholeprize` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
