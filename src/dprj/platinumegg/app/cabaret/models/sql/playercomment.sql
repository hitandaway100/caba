alter table `cabaret_playercomment` add constraint `playercomment_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
