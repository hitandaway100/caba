CREATE INDEX shareseriallog_uid_mid on cabaret_shareseriallog(`uid`,`mid`);
CREATE INDEX shareseriallog_mid_itime on cabaret_shareseriallog(`mid`,`itime`);
alter table `cabaret_shareseriallog` add constraint `shareseriallog_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_serialcampaignmaster(`id`) ON DELETE CASCADE;
