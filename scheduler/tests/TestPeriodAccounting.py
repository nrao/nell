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

from scheduler.models         import Period_Accounting
from test_utils              import BenchTestCase, timeIt

class TestPeriodAccounting(BenchTestCase):

    def test_1(self):
       # all zero times
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()

        fields = pa.getFloatFields()
        for f in fields:
            self.assertEquals(0.0, pa.get_time(f))

        # just scheduled time
        pa.set_changed_time("scheduled", 4.0)
        pa.save()
        nonzero = ["scheduled", "observed", "time_billed"]
        for f in fields:
            if f not in nonzero:
                self.assertEquals(0.0, pa.get_time(f))
        for f in nonzero:        
            self.assertEquals(4.0, pa.get_time(f))

        # now lose some time
        pa.set_changed_time("lost_time_weather", 1.0)    
        self.assertEquals((True, None), pa.validate())
        pa.save()
        nonzero.extend(["lost_time_weather", "lost_time"])
        for f in fields:
            if f not in nonzero:
                self.assertEquals(0.0, pa.get_time(f))
        self.assertEquals(pa.get_time("scheduled"), 4.0)    
        self.assertEquals(pa.get_time("observed"),  3.0)    
        self.assertEquals(pa.get_time("time_billed"),  3.0)    
        self.assertEquals(pa.get_time("lost_time_weather"), 1.0)    
        self.assertEquals(pa.get_time("lost_time"), 1.0)    

        # loss too much time
        pa.set_changed_time("lost_time_weather", 100.0)    
        msg = (False, 'time_billed cannot be negative.  Please check times.')
        self.assertEquals(msg, pa.validate())
        pa.set_changed_time("lost_time_weather", 1.0)

        # misc
        pa.lost_time_bill_project = 1.0
        pa.not_billable = 1.0
        self.assertEquals((True, None), pa.validate())
        pa.save()
        nonzero.extend(["lost_time_bill_project", "not_billable"])
        for f in fields:
            if f not in nonzero:
                self.assertEquals(0.0, pa.get_time(f))
        self.assertEquals(pa.get_time("scheduled"), 4.0)    
        self.assertEquals(pa.get_time("observed"),  3.0)    
        self.assertEquals(pa.get_time("time_billed"),  2.0)    
        self.assertEquals(pa.get_time("lost_time_weather"), 1.0)    
        self.assertEquals(pa.get_time("lost_time"), 1.0)

    def test_update_from_post(self):

       # all zero times
        pa = Period_Accounting(scheduled = 0.0)
        pa.save()

        fields = pa.getFloatFields()
        for f in fields:
            self.assertEquals(0.0, pa.get_time(f))

        fdata = {}
        pa.update_from_post(fdata)
        for f in fields:
            self.assertEquals(0.0, pa.get_time(f))

        fdata = {"scheduled" : 4.0
               , "lost_time_weather" : 1.0
               , "lost_time_bill_project" : 1.0
               , "not_billable" : 1.0
                 }
        pa.update_from_post(fdata)
        nonzero = fdata.keys()
        nonzero.extend(["observed"
                      , "lost_time"
                      , "time_billed"])
        for f in fields:
            if f not in nonzero:
                self.assertEquals(0.0, pa.get_time(f))
        self.assertEquals(pa.get_time("scheduled"), 4.0)    
        self.assertEquals(pa.get_time("observed"),  3.0)    
        self.assertEquals(pa.get_time("time_billed"),  2.0)    
        self.assertEquals(pa.get_time("lost_time_weather"), 1.0)    
        self.assertEquals(pa.get_time("lost_time"), 1.0)

