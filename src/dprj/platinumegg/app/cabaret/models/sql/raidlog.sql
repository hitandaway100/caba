CREATE INDEX raidlog_uid_ctime on cabaret_raidlog(`uid`,`ctime`);
CREATE INDEX raidlog_uid_raidid on cabaret_raidlog(`uid`,`raidid`);
ALTER TABLE `cabaret_raidlog` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
