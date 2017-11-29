alter table `cabaret_raideventraidmaster` add constraint `raideventraidmaster_eventid` FOREIGN KEY (`eventid`) REFERENCES cabaret_raideventmaster(`id`) ON DELETE CASCADE;
