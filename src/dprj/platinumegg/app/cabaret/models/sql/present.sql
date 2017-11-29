CREATE INDEX present_toid_ctime on cabaret_present(`toid`,`limittime`);
alter table `cabaret_present` add constraint `present_toid` FOREIGN KEY (`toid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
