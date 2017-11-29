CREATE INDEX greetlog_toid_gtime on cabaret_greetlog(`toid`,`gtime`);
CREATE INDEX greetlog_toid_fromid_gtime on cabaret_greetlog(`toid`,`fromid`,`gtime`);
alter table `cabaret_greetlog` add constraint `greetlog_fromid` FOREIGN KEY (`fromid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_greetlog` add constraint `greetlog_toid` FOREIGN KEY (`toid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
