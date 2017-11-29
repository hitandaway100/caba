ALTER TABLE cabaret_reprinttickettradeshopmaster ADD (stock int(10) DEFAULT 0 NOT NULL);
ALTER TABLE cabaret_reprinttickettradeshopmaster ADD (reprintticket_trade_text int(10) DEFAULT 0 NOT NULL);
ALTER TABLE cabaret_reprinttickettradeshopmaster ADD (priority smallint(5) unsigned DEFAULT 0 NOT NULL);
ALTER TABLE cabaret_reprinttickettradeshopmaster MODIFY stock int(10) unsigned DEFAULT 0 NOT NULL;
ALTER TABLE cabaret_reprinttickettradeshopmaster MODIFY reprintticket_trade_text int(10) unsigned DEFAULT 0 NOT NULL;
