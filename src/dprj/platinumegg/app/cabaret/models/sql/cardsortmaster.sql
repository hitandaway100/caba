CREATE INDEX cardsortmaster_hklevel_ctype_rare on cabaret_cardsortmaster(`hklevel`,`ctype`,`rare`);
CREATE INDEX cardsortmaster_hklevel_rare on cabaret_cardsortmaster(`hklevel`,`rare`);
alter table `cabaret_cardsortmaster` add constraint `cardsortmaster_id` FOREIGN KEY (`id`) REFERENCES cabaret_cardmaster(`id`) ON DELETE CASCADE;
create view cabaret_cardmasterview(`id`,`pubstatus`,`edittime`,`name`,`text`,`thumb`,`ckind`,`gtype`,`cost`,`basepower`,`maxpower`,`maxlevel`,`skill`,`albumhklevel`,`basematerialexp`,`maxmaterialexp`,`baseprice`,`maxprice`,`evolcost`,`ctype`,`rare`,`album`,`hklevel`, `dmmurl`) as select a.`id`,a.`pubstatus`,a.`edittime`,a.`name`,a.`text`,a.`thumb`,a.`ckind`,a.`gtype`,a.`cost`,a.`basepower`,a.`maxpower`,a.`maxlevel`,a.`skill`,a.`albumhklevel`,a.`basematerialexp`,a.`maxmaterialexp`,a.`baseprice`,a.`maxprice`,a.`evolcost`,b.`ctype`,b.`rare`,b.`album`,b.`hklevel`,a.`dmmurl` from cabaret_cardmaster as a left join cabaret_cardsortmaster as b on a.id=b.id;