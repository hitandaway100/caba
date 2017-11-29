CREATE INDEX card_uid_mid on cabaret_card(`uid`,`mid`);
alter table `cabaret_card` add constraint `card_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_card` add constraint `card_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_cardmaster(`id`) ON DELETE CASCADE;
