# This is part of coursework of Software Engineering, 2013.02-2013.07
# Source code by Pengyu CHEN (cpy.prefers.you[at]gmail.com)
# COPYLEFT, ALL WRONGS RESERVED

def data_import(dbpath):
    import sqlite3
    import os
    
    cwd = os.getcwd()
    fwd = __file__[:-__file__[::-1].index('/')]
    os.chdir(fwd)

    conn = sqlite3.connect(dbpath)
    
    f = open("fetched_flights", "r")
    lines = f.readlines()
    f.close()
    
    for line in lines:
        l = line[:-1].split(',')
        conn.execute(
            "INSERT INTO flight VALUES(?,?,?,?,?,?,?,?,?,?,?)", 
            [
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

    f = open('airport_list', 'r')
    lines = f.readlines()
    f.close()

    for line in lines:
        l = line[:-1].split(' ')
        conn.execute(
            'INSERT INTO airport VALUES(?,?,?,?,?)',
            [
                l[0],   # code
                l[2],   # city
                l[1],   # name_cn
                "",     # name_en
                1,      # domestic
            ]
        )
    
    f = open('airline_list', 'r')
    lines = f.readlines()
    f.close()

    for line in lines:
        l = line[:-1].split(',')
        conn.execute(
            'INSERT INTO airline VALUES(?,?,?,?)',
            [
                l[0],   # code
                l[1],   # name_cn
                l[2],   # name_en
                l[3],   # country_cn
            ]
        )
     


    conn.commit()
    conn.close()
    os.chdir(cwd)
    print("fetched flights inserted into dbfile. :)")

if __name__ == "__main__":
    data_import("./dbfile")
