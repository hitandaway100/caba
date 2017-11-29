alter table `cabaret_battleeventpresentmaster` add constraint `battleeventpresentmaster_eventid` FOREIGN KEY (`eventid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
