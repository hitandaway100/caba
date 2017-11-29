CREATE INDEX serialcode_uid_mid on cabaret_serialcode(`uid`,`mid`);
CREATE INDEX serialcode_mid_itime on cabaret_serialcode(`mid`,`itime`);
alter table `cabaret_serialcode` add constraint `serialcode_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_serialcampaignmaster(`id`) ON DELETE CASCADE;
