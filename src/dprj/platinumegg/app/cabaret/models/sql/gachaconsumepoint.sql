alter table `cabaret_gachaconsumepoint` add constraint `consumepoint_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_gachaconsumepoint` add constraint `consumepoint_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_gachamaster(`id`) ON DELETE CASCADE;
