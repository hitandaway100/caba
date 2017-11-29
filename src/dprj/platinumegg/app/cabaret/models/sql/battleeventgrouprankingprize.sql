CREATE INDEX `battleeventgrouprankingprize_mid_fixed` on cabaret_battleeventgrouprankingprize(`mid`,`fixed`);
alter table `cabaret_battleeventgrouprankingprize` add constraint `battleeventgrouprankingprize_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventgrouprankingprize` add constraint `battleeventgrouprankingprize_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
