CREATE INDEX userlogevolution_uid_ctime on cabaret_userlogevolution(`uid`,`ctime`);
ALTER TABLE `cabaret_userlogevolution` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
