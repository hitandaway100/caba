alter table `cabaret_rankinggachaclose` add constraint `rankinggachaclose_id` FOREIGN KEY (`id`) REFERENCES cabaret_rankinggachamaster(`id`) ON DELETE CASCADE;
