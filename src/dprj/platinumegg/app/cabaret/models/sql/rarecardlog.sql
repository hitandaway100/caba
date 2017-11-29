alter table `cabaret_rarecardlog` add constraint `rarecardlog_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
