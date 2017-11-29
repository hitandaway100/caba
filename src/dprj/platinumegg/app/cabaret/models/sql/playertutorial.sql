alter table `cabaret_playertutorial` add constraint `playertutorial_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
