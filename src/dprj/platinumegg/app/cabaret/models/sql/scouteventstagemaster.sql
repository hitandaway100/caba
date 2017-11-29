CREATE INDEX scouteventstagemaster_eventid_area on cabaret_scouteventstagemaster(`eventid`,`area`);
CREATE INDEX scouteventstagemaster_eventid_stage on cabaret_scouteventstagemaster(`eventid`,`stage`);
alter table `cabaret_scouteventstagemaster` add constraint `scouteventstagemaster_eventid` FOREIGN KEY (`eventid`) REFERENCES cabaret_scouteventmaster(`id`) ON DELETE CASCADE;
