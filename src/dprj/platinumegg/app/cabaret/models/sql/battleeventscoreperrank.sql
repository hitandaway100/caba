alter table `cabaret_battleeventscoreperrank` add constraint `battleeventscoreperrank_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventscoreperrank` add constraint `battleeventscoreperrank_eventid` FOREIGN KEY (`eventid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
