alter table `cabaret_serialcount` add constraint `serialcount_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_serialcount` add constraint `serialcount_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_serialcampaignmaster(`id`) ON DELETE CASCADE;
