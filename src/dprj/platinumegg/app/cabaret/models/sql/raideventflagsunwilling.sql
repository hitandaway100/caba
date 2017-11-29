alter table `cabaret_raideventflagsunwilling` add constraint `raideventflagsunwilling_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_raideventflagsunwilling` add constraint `raideventflagsunwilling_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_raideventmaster(`id`) ON DELETE CASCADE;
