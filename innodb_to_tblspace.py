#!/usr/bin/env python3

""" rewrite ENGINE in table design """

FIN = open("standard.sql", "rb")
FOUT = open("ndb.sql", "wb")
IDX = 1
LINE = None

for LINE in FIN:
    if "-- Current Database: `bingo_core`" in LINE:
        print("switching to bingo_core")
        IDX = 1
    elif "-- Current Database: `game_server`" in LINE:
        print("switching to game_server")
        IDX = 1
    elif "-- Current Database: `wallet`" in LINE:
        print("switching to wallet")
        IDX = 1
    elif "-- Current Database:" in LINE:
        print("switching to unkown database")
        IDX = 0
    LINE = LINE.replace("ENGINE=MyISAM", "TABLESPACE TS1 STORAGE DISK ENGINE=NDBCLUSTER")
    LINE = LINE.replace("ENGINE=InnoDB", "TABLESPACE TS1 STORAGE DISK ENGINE=NDBCLUSTER")

if IDX != 0:
    FOUT.write(LINE)

FIN.close()
FOUT.close()
