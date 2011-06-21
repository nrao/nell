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

from django.db        import models
from django.db.models import Q
from datetime         import datetime, timedelta
from Semester         import Semester
from Project          import Project

# This class is responsible for providing boiler plate email
# text for the Project Email Dialog in the Scheduler's Tools.

# Email Templates are currently read only, so we won't bother
# with a full REST interface, with the NellResource, etc.

class EmailTemplate(models.Model):
    name    = models.CharField(null = True, blank = True, max_length = 32)
    subject = models.CharField(null = True, blank = True, max_length = 150)
    body    = models.TextField(null = True, blank = True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        if len(self.body) > 10:
            body = self.body[:10] + "..."
        else:
            body = self.body
        return "%s = subj: %s, body: %s" % (self.name, self.subject, body)

    def json_dict(self):
        return {"name"    : self.name
              , "subject" : self.subject
              , "body"    : self.body
               }
      
    def evaluate(self, project):
        """
        Take this templates subject and body, and substitute keys
        with values from the given project, using the mapping.
        Note: Conveniently, this returns a dictionary of the
        evaluated template that doubles as JSON.
        """

        map = self.get_mapping(project)
        email = {"name" : self.name}
        fields = ["subject", "body"]
        for fieldName in fields:
            field = self.__getattribute__(fieldName)
            for key in map.keys():
                if field.find(key) != -1:
                    field = field.replace(key, map[key])
            email[fieldName] = field
        return email    

    def get_mapping(self, project):
        "Dict used for evaluating templates."

        thisSem = Semester.getCurrentSemester()
        nextSem = Semester.getFutureSemesters()[0]
        fmt = "%Y-%m-%d"
        map = {"<pcode>" : project.pcode
             , "<start_this_semester>" : thisSem.start().strftime(fmt)
             , "<end_this_semester>"   : thisSem.end().strftime(fmt)
             , "<start_next_semester>" : nextSem.start().strftime(fmt)
             , "<end_next_semester>"   : nextSem.end().strftime(fmt)
              }
        return map

    @staticmethod
    def get_templates(pcodes):
        """
        Given the list of project pcodes, retrieves project info,
        formats the templates, and returns them.
        """

        # get the project(s)
        qset = Q()
        for pcode in pcodes:
            qset |= Q(pcode=pcode)
        projs = Project.objects.filter(qset)
        
        if len(projs) != 1:
            # the blank template is the only one supported
            return [EmailTemplate.blank_template().json_dict()]
            
        # otherwise, take the one project, and use it to evaluate
        # the templates
        p = projs[0]
        return [template.evaluate(p) for template in EmailTemplate.objects.all()]
        
    @staticmethod
    def blank_template():
        return EmailTemplate.objects.get(name = "Blank")

    class Meta:
        db_table  = "email_templates"
        app_label = "scheduler"
      
