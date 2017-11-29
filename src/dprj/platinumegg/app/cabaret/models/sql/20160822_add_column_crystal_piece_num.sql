ALTER TABLE cabaret_prizemaster ADD (crystal_piece_num int(10) DEFAULT 0 NOT NULL);
ALTER TABLE cabaret_trademaster ADD (is_used_crystal_piece tinyint(1) DEFAULT 0 NOT NULL);
