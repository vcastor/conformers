#!/usr/bin/python3
import sqlite3

con = sqlite3.connect('nucleo_data.db')
cur = con.cursor()

cur.execute("SELECT smiles,solvent,comment FROM main")
data = cur.fetchall()
cur.executemany("UPDATE reactive_msc SET comment=? WHERE smiles=? AND solvent=?",[(cm,sm,sv)for sm,sv,cm in data])

con.commit()
con.close()

