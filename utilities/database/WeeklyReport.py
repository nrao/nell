from django.core.management import setup_environ
import settings
setup_environ(settings)

from sesshuns.models import *
from sets            import Set
from datetime import date,datetime,timedelta

def overlap(start1,dur1,start2,dur2):
    end1=start1+timedelta(seconds=dur1*60*60)
    end2=start2+timedelta(seconds=dur2*60*60)
    return start1<end2 and start2<end1

def projects_list(start_date,no_days,sorted_projects):
    end_date=start_date+timedelta(seconds=no_days*24*60*60)
    return Set([p for p in sorted_projects for s in p.sesshun_set.all() for P in s.period_set.all() if overlap(P.start,P.duration,start_date,no_days*24)])

def session_type(start_date,no_days,p):
    end_date=start_date+timedelta(seconds=no_days*24*60*60)
    session_list=[s for s in p.sesshun_set.all() for P in s.period_set.all() if overlap(P.start,P.duration,start_date,no_days*24)]
    return Set([s.session_type.type for s in session_list])
    #session_type_list=[]
    #for s in session_list:
    #    if s.session_type.type not in session_type_list:
    #        session_type_list.append(s.session_type.type)
    #return session_type_list

def projects_list_month(sorted_projects,month):
    
    return Set([p for p in sorted_projects for s in p.sesshun_set.all() for P in s.period_set.all() if (P.start.month==month and P.start.year==datetime.today().year) or ((P.start+timedelta(seconds=P.duration*60*60)).month==month and (P.start+timedelta(seconds=P.duration*60*60)).year==datetime.today().year)])
def print_outfile(list_1,list_2,outfile):
    str_list=["Astronomy","Maintenance","Test & Comm","Shutdown"]
    for i in range(0,len(str_list)):
        outfile.write("\n"+str_list[i].ljust(13)+"\t"+str(list_1[i])+"\t"+str(list_2[i]))
 

def no_hours(s,hrs):
    
    #for P in p:
    #    for s in P.sesshun_set.all():
    for per in s.period_set.all():
        end=per.start+timedelta(seconds=per.duration*60*60)
        if per.start<datetime.today() and end<datetime.today():
            duration=0
        if per.start<datetime.today() and end>datetime.today():
            duration_s=end-datetime.today()
            duration=duration_s.days*24+duration_s.seconds/(60.0*60)
        if per.start>=datetime.today():
            duration=per.duration
        hrs=hrs+duration
    return hrs
def no_hours_trimester(s,hrs,trimester_end):
    
    #for P in p:
    #    for s in P.sesshun_set.all():
    for per in s.period_set.all():
        end=per.start+timedelta(seconds=per.duration*60*60)
        if per.start<datetime.today() and end<datetime.today():
            duration=0
        if end<trimester_end:
            if per.start<datetime.today() and end>datetime.today():
                duration_s=end-datetime.today()
                duration=duration_s.days*24+duration_s.seconds/(60*60)
            if per.start>=datetime.today():
                duration=per.duration
        else:
            if per.start<datetime.today() and end>datetime.today():
                duration_s=trimester_end-datetime.today()
                duration=duration_s.days*24+duration_s.seconds/(60*60)
            elif per.start>=datetime.today() and per.start<trimester_end:
                duration_s=trimester_end-per.start
                duration=duration_s.days*24+duration_s.seconds/(60*60)
            else:
                duration=0
        hrs=hrs+duration
    return hrs

def disp(m,sorted_projects):
    proj_list=[]
    hrs=0
    for p in sorted_projects:
        if not p.complete:
            for s in p.sesshun_set.all():
                for per in s.period_set.all():
                    if per.start.year==m:
                        end=per.start+timedelta(seconds=per.duration*60*60)
                        if per.start<datetime.today() and end<datetime.today():
                            duration=0
                        if per.start<datetime.today() and end>datetime.today():
                            duration_s=end-datetime.today()
                            duration=duration_s.days*24+duration_s.seconds/(60.0*60)
                        if per.start>=datetime.today():
                            duration=per.duration
                        hrs=hrs+duration
                        if not p in proj_list:
                            proj_list.append(p)
    string=  str(m)+":"+str(hrs)+"("+str(len(proj_list))+")"
    return string

def scheduled(p_list,p_list1,outfile):
    list_1=calc_hrs(p_list)
    list_2=calc_hrs(p_list1)
    print_outfile(list_1,list_2,outfile)

def calc_hrs(p_list):
    astronomy=sum([P.accounting.scheduled for p in p_list if p.project_type.type=='science' for s in p.sesshun_set.all() for P in s.period_set.all()])
    maintenance=sum([P.accounting.scheduled for p in p_list if p.pcode=='Maintenance' for s in p.sesshun_set.all() for P in s.period_set.all()])
    test=sum([P.accounting.scheduled for p in p_list if p.pcode[0]=='T' for s in p.sesshun_set.all() for P in s.period_set.all()])
    shutdown=sum([P.accounting.scheduled for p in p_list if p.pcode=='Shutdown' for s in p.sesshun_set.all() for P in s.period_set.all()])
    return [astronomy,maintenance,test,shutdown]  
        
def GenerateProjectReport():
    outfile=open("./WeeklyReport.txt",'w')
    outfile.write("Last 7 days ("+str(datetime.today().date())+" to "+ str((datetime.today()+timedelta(seconds=7*24*60*60)).date())+")")
    outfile.write("\n=======================================")
    outfile.write("\n Observations for proposals")
    sorted_projects = sorted(Project.objects.all(), lambda x, y: cmp(x.pcode,y.pcode))
    values=projects_list(datetime.today(),7,sorted_projects)
    if not values:
        outfile.write("\n\tNone")
    else:
        for p in values:
            outfile.write("\n\t"+p.pcode)
    outfile.write("\nCompleted proposals")
    value=[p for v in values if p.complete] 
    if not value:
        outfile.write("\n\tNone")
    else:
        for p in values:
            if p.complete:
                outfile.write("\n\t"+p.pcode)
    outfile.write("\n\nNext Week")
    outfile.write("\n============")
    p_list=sorted(projects_list(datetime.today()+timedelta(seconds=7*24*60*60),7,sorted_projects),lambda x,y:cmp(x.pcode,y.pcode))
    if not p_list:
        outfile.write("\n\tNone")
    else:
        for p in p_list:
            outfile.write("\n\t"+p.pcode.ljust(11))
            for s in session_type(datetime.today()+timedelta(seconds=7*24*60*60),7,p):
                outfile.write("\t"+s.center(9))
            outfile.write("\t"+str(p.principal_investigator()))
            outfile.write("\n\t"+p.name)
    outfile.write("\n\n Contact Information")
    outfile.write("\n======================")
    outfile.write("\nProposal \t\tPI\t\t  Email [NRAO contact]")
    outfile.write("\n----------------------------------------------------------------------")
    if not p_list:
        outfile.write("\n\tNone")
    else:
        for p in p_list:
            outfile.write("\n"+p.pcode.ljust(11)+"\t"+str(p.principal_investigator()).center(20)+ "\t"+str(p.principal_investigator().getStaticContactInfo()['emails'][0]))
        
            outfile.write(" ["+ str(p.friend)+"]")
    outfile.write("\n\nScheduled Hours [backup]")
    outfile.write("\n============================")
    prev_month=date(datetime.today().year,datetime.today().month-1,1)
    outfile.write("\n\t\t"+prev_month.strftime("%B"))
    outfile.write("\t"+datetime.today().strftime("%B"))
    p_list=sorted(projects_list_month(sorted_projects,datetime.today().month),lambda x,y:cmp(x.pcode,y.pcode))
    p_list1=sorted(projects_list_month(sorted_projects,datetime.today().month-1),lambda x,y:cmp(x.pcode,y.pcode))
    scheduled(p_list1,p_list,outfile)
    S=sorted([s for s in Semester.objects.all() if s.start()<=datetime.today() and s.end()>datetime.today()],lambda x,y : cmp(x.start(),y.start()))[0]
    trimester_end=S.end()#datetime(2010,1,1,0,0,0)
    hr=0
    for p in sorted_projects:
        if not p.complete:
            for s in p.sesshun_set.all():
                hrs=no_hours_trimester(s,hr,trimester_end)
                hr=hrs
    outfile.write("\n\ncurrent backlog of Reg & RSS proposals = "+str(hr))
   
    p=[per.start.year for per in Period.objects.all()]
    m=min(p)
    for x in range(0,max(p)-min(p)+1):
        outfile.write("\n\t"+str(disp(m,sorted_projects)))
        m=m+1
        
    hr=0
    for p in Project.objects.all():
        if not p.complete:
            for s in p.sesshun_set.all():
                if s.session_type.type!="open" and s.session_type.type!="vlbi":
                     hrs=no_hours_trimester(s,hr,trimester_end)
                     hr=hrs
    outfile.write("\n\tBacklog includes "+str(hr)+" hrs of monitoring projects")
    hr=0
    for p in Project.objects.all():
        if not p.complete:
            for s in p.sesshun_set.all():
                if s.session_type.type=="vlbi":
                     hrs=no_hours_trimester(s,hr,trimester_end)
                     hr=hrs
    outfile.write("\n\tBacklog includes "+str(hr)+" hrs of vlbi projects")
    projects=[p for p in sorted_projects if not p.complete]
    hr=0
    for p in sorted_projects:
        if not p.complete:
            for s in p.sesshun_set.all():
                hrs=no_hours(s,hr)
                hr=hrs
            
    outfile.write("\n Total time to Discharge [hours]"+str(hr))
    not_open_vlbi=[]
    for p in sorted_projects:
        if not p.complete:
            for s in p.sesshun_set.all():
                if (s.session_type.type!="open") and  s.session_type.type!="vlbi": 
                    if p not in not_open_vlbi:
                        not_open_vlbi.append(p)
    hr=0
    for p in Project.objects.all():
        if not p.complete:
            for s in p.sesshun_set.all():
                if s.session_type.type!="open" and s.session_type.type!="vlbi":
                     hrs=no_hours(s,hr)
                     hr=hrs
                       

    outfile.write("\n\tIncludes "+str(hr)+" of monitoring (not Large or Spec) after trimester ")
    l=[]
    for p in sorted_projects:
        hr=0
        if not p.complete:
            for s in p.sesshun_set.all():
                for per in s.period_set.all():
                    end =per.start+timedelta(seconds=per.duration*60*60)
                    if per.start<datetime.today() and end<datetime.today():
                        duration=0
                    if per.start<datetime.today() and end>datetime.today():
                        duration_s=end-datetime.today()
                        duration=duration_s.days*24+duration_s.seconds/(60.0*60)
                    if per.start>=datetime.today():
                        duration=per.duration
                    hr=hr+duration
        l.append(hr)
    hr=0
    for li in l:
        if li>200:
            hr=hr+li
    outfile.write("\n\t"+str(hr)+" hours of large proposals")
    hr=0
    for p in Project.objects.all():
        if not p.complete:
            for s in p.sesshun_set.all():
                if s.session_type.type=="vlbi":
                     hrs=no_hours(s,hr)
                     hr=hrs
    outfile.write("\n\t"+str(hr)+" hrs of vlbi proposals")
    
    
if __name__=='__main__':
    GenerateProjectReport()
