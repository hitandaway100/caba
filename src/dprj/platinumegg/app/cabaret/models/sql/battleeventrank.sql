CREATE INDEX `battleeventrank_mid_rank_next` on cabaret_battleeventrank(`mid`,`rank_next`);
alter table `cabaret_battleeventrank` add constraint `battleeventrank_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventrank` add constraint `battleeventrank_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
