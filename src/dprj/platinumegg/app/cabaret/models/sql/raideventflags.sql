alter table `cabaret_raideventflags` add constraint `raideventflags_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_raideventflags` add constraint `raideventflags_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_raideventmaster(`id`) ON DELETE CASCADE;
