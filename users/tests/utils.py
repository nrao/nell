######################################################################
#
#  TestMaintenanceActivityGroup.py
#
#  Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#  Correspondence concerning GBT software should be addressed as follows:
#  GBT Operations
#  National Radio Astronomy Observatory
#  P. O. Box 2
#  Green Bank, WV 24944-0002 USA
#
######################################################################

from users.models import *
from scheduler.models import *
from datetime import datetime

def create_maintenance_activity():
     # receivers for receiver swap
    old_receiver = Receiver.objects.filter(id = 8)[0]
    new_receiver = Receiver.objects.filter(name = "Rcvr26_40")[0]
    #zpectrometer backend
    zpect_be = Backend.objects.filter(abbreviation = "Zpect")[0]        
    #create a maintenance activity
    ma = Maintenance_Activity(subject =  "Test Maintenance Activity")
    ma.save()
    ma.set_location("Upstairs, Downstairs")
    ma.set_telescope_resource(Maintenance_Telescope_Resources.objects.filter(id = 6)[0])
    ma.set_software_resource(Maintenance_Software_Resources.objects.filter(id = 5)[0])
    ma.add_receiver(old_receiver)
    ma.add_receiver(new_receiver)
    ma.add_backend("DCR") # can name the backend, or...
    ma.add_backend(zpect_be) # add a backend object
    ma.add_receiver_change(old_receiver, new_receiver)
    ma.set_description("Breakn' shit.")
    ma.contacts = "me"
    ma.save()
    created_by = Maintenance_Activity_Change()
    created_by.responsible = "me"
    created_by.date = datetime.now()
    created_by.save()
    ma.modifications.add(created_by)
    ma.save()
    
    return ma

