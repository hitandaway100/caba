ALTER TABLE cabaret_infomationmaster ADD (jumpto varchar(48) DEFAULT "" NULL);
ALTER TABLE cabaret_infomationmaster ADD (imageurl varchar(1000) DEFAULT "" NULL);
ALTER TABLE cabaret_prizemaster ADD (crystal_piece_num int(10) DEFAULT 0 NOT NULL);
ALTER TABLE cabaret_trademaster ADD (is_used_crystal_piece tinyint(1) DEFAULT 0 NOT NULL);
