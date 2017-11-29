CREATE INDEX `battleeventgroup_eventid_cdate` on cabaret_battleeventgroup(`eventid`,`cdate`);
CREATE INDEX `battleeventgroup_rankid_fixed_level_max` on cabaret_battleeventgroup(`rankid`,`fixed`,`level_max`);
alter table `cabaret_battleeventgroup` add constraint `battleeventgroup_eventid` FOREIGN KEY (`eventid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventgroup` add constraint `battleeventgroup_rankid` FOREIGN KEY (`rankid`) REFERENCES cabaret_battleeventrankmaster(`id`) ON DELETE CASCADE;
