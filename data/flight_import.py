# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

def flight_import(dbpath, flightpath):
    import sqlite3
    f = open(flightpath, "r")
    lines = f.readlines()
    f.close()

    conn = sqlite3.connect(dbpath)

    for line in lines:
        l = line[:-1].split(',')
        conn.execute(
            "INSERT INTO flight VALUES(?,?,?,?,?,?,?,?,?,?,?)", [
            l[0],
            0,
            0,
            l[2], # airport 1
            l[3], # time 1
            l[5], # airport 2
            l[6], # time 2
            l[7], # aircraft
            l[8], # on days
            l[10], # punctuality
            { "True": 1, "False": 0}[l[11]]
            ]
            )
    conn.commit()
    conn.close()
    print("fetched flights inserted into dbfile. :)")

if __name__ == "__main__":
    flight_import("./dbfile", "fetched_flights")
