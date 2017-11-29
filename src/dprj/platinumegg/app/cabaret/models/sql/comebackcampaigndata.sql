ALTER TABLE `cabaret_comebackcampaigndata` ADD CONSTRAINT `comebackcampaigndata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
ALTER TABLE `cabaret_comebackcampaigndata` ADD CONSTRAINT `comebackcampaigndata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_comebackcampaignmaster(`id`) ON DELETE CASCADE;
