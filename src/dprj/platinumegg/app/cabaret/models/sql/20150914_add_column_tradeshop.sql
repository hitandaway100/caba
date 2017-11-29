ALTER TABLE cabaret_tradeshopitemmaster ADD (ticketname varchar(48) DEFAULT "" NULL);
ALTER TABLE cabaret_tradeshopitemmaster ADD (ticketthumb varchar(48) DEFAULT "" NULL);
ALTER TABLE cabaret_tradeshopitemmaster ADD (pt_change_text int(10) DEFAULT 0 NOT NULL);
ALTER TABLE cabaret_tradeshopitemmaster ADD (additional_ticket_id int(10) DEFAULT 0 NULL);
