#!/usr/bin/python3
import os
import sqlite3
# Try to use split or create your own function, the " re " library should be avoided
# since it has troubles with @, # that are so common in the smile notation

# Database file path
db_file_path = 'entropiesCOSMO.db'

# Connect to SQLite database (this will create the database if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Retrieve all molecule names from the database
# cursor.execute('SELECT molecule_name, natoms FROM PBE0 WHERE nconformers > 1')
# molecules = cursor.fetchall()
molecules = [('PENTANOL', 30)]

for molecule, atoms in molecules:
    if molecule == "2,2'-Dimethylbiphenyl":
        outfile = "2,2-Dimethylbiphenyl"
    else:
        outfile = molecule
    freqfiles = os.path.join('..', 'work_dir', molecule) + '/Fre*/Freq*out'
    outfile = os.path.join('.', 'pbe', 'output_files', outfile+'.out')
    if os.path.exists(outfile):# and atoms is None:
        cmd = f'grep "Electrophilicity index (w=omega)" {freqfiles}'
        omega = os.popen(cmd).read().split('\n')[:-1]
        omega.sort(key=lambda x: (x.split('/')[-2], int(x.split('/')[-2].split('.')[1]) if '.' in x.split('/')[-2] else 0))
        cmd = f'grep Weight {outfile}'
        weight = os.popen(cmd).read().split('\n')[:-1]
        w = 0
        for i in range(len(omega)):
            iomega = omega[i].split()[-1]
            iweight = weight[i].split()[-1]
            w += float(iomega)*float(iweight)
        print(molecule, w)
        # cursor.execute('UPDATE PBE0 SET omega = ? WHERE molecule_name = ?', (w, molecule))

# Commit the changes and close the connection
conn.commit()
conn.close()

print('End of script')

