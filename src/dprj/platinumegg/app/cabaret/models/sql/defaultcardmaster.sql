alter table `cabaret_defaultcardmaster` add constraint `card_leader` FOREIGN KEY (`leader`) REFERENCES cabaret_cardmaster(`id`) ON DELETE CASCADE;
