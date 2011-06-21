# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

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
