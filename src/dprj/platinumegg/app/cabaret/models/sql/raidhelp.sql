CREATE INDEX raidhelp_toid_etime on cabaret_raidhelp(`toid`,`etime`);
CREATE INDEX raidhelp_raidid_toid on cabaret_raidhelp(`raidid`,`toid`);
ALTER TABLE `cabaret_raidhelp` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
