alter table `cabaret_playerrequest` add constraint `playerrequest_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
