import os
from database_backup import ndaysold

def tmp_filter(file):
    "used for dev."
    return "2010-10-04" not in file 

if __name__ == "__main__":

    db_bkup_dir = "/home/dss/database_backups"
    files2archive = ["%s" % f for f in os.listdir(db_bkup_dir) if 'dss.' in f and ndaysold(2, 'dss', f) and tmp_filter(f)]

    cmd = "gzip -d %s/dss_backups.tar.gz" % db_bkup_dir
    print cmd
    os.system(cmd)

    cmd = "tar -rf %s/dss_backups.tar %s "  % (db_bkup_dir, " ".join(files2archive))
    print cmd
    os.system(cmd)

    cmd = "gzip -c %s/dss_backups.tar > %s/dss_backups.tar.gz" % (db_bkup_dir, db_bkup_dir)
    print cmd
    os.system(cmd)

    cmd = "rm %s/dss_backups.tar" % db_bkup_dir
    print cmd
    os.system(cmd)

    for f in files2archive:
        cmd = "rm %s/%s" % (db_bkup_dir, f)
        print cmd
        os.system(cmd)
