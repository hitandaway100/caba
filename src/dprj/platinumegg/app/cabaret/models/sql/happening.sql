CREATE INDEX happening_state_etime on cabaret_happening(`state`,`etime`);
ALTER TABLE `cabaret_happening` DROP PRIMARY KEY, ADD PRIMARY KEY(`id`,`ctime`);
