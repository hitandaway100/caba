CREATE INDEX treasurebronze_uid_etime on cabaret_treasurebronze(`uid`,`etime`);
ALTER TABLE `cabaret_treasurebronzeopened` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`otime`);
