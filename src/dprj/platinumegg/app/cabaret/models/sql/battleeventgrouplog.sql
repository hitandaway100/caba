alter table `cabaret_battleeventgrouplog` add constraint `battleeventgrouplog_eventid` FOREIGN KEY (`eventid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventgrouplog` add constraint `battleeventgrouplog_rankid` FOREIGN KEY (`rankid`) REFERENCES cabaret_battleeventrankmaster(`id`) ON DELETE CASCADE;
