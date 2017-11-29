alter table `cabaret_scouteventpresentprizemaster` add constraint `scouteventpresentprizemaster_eventid` FOREIGN KEY (`eventid`) REFERENCES cabaret_scouteventmaster(`id`) ON DELETE CASCADE;
