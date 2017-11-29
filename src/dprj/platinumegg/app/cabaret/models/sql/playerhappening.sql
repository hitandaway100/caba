alter table `cabaret_playerhappening` add constraint `playerhappening_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
