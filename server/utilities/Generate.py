from datetime import timedelta
from math     import asin, sin
from random   import choice, randint, random, uniform
import slalib

from server.sesshuns.models import *

between_dist    = [4, 8, 10, 24, 48]
freq_dist       = [2, 3, 5, 8, 13, 21, 34, 55]
grade_dist      = [2.0, 3.0, 4.0, 4.0, 4.0, 4.0]
semester        = 2
total_time_dist = [2, 2, 3, 3, 4, 4, 4, 6, 6, 6, 8, 8, 10]
trimesterMonth  = [3,1,1,1,1,2,2,2,2,3,3,3]

class Generate(object):

    def __init__(self, year, ratio, total_avaliable):
        self.sky_types = 'geegeegeeaaa'  # sssa, s <- gee
        self.galactic_center_proportion = .2
        self.bands = [
            'kkqqaaxuccslllllllll'  # 0 => backup
          , 'kkkqqaaxuccsslllllll'  # 1
          , 'kqqaxucsllllllllllll'  # 2
          , 'kkqqaaaxxuccslllllll'  # 3
          ]

        self.frequencies = dict(
            # assume we are observing the water line 40% of the time
            k = lambda: random() < 0.40 and 22.2 or uniform(18.0, 26.0)
          , q = lambda: uniform(40.0, 50.0)
          , a = lambda: uniform(26.0, 40.0)
          , x = lambda: uniform(8.0, 10.0)
          , u = lambda: uniform(12.0, 15.4)
          , c = lambda: uniform(3.95, 5.85)
          , s = lambda: uniform(2.0, 3.95)
          , l = lambda: uniform(1.15, 1.73)
          )
        # Windowed interval / period distribution, e.g., (14, 3) indicates
        # every two weeks select session in a 3-day window.
        self.windowed_interval_period_distribution = \
                    [(7, 3), (14, 3), (30, 7), (30, 5), (30, 5)]

        self.year = year
        o, f, w = [r * total_avaliable for r in ratio]
        self.open_time      = o
        self.fixed_time     = f
        self.windowed_time  = w
        
        self.project        = first(Project.objects.all())
        self.fixed_type     = first(Session_Type.objects.filter(type = "fixed"))
        self.windowed_type  = first(Session_Type.objects.filter(type = "windowed"))
        self.observing_type = first(Observing_Type.objects.filter(type = "spectral line"))
        self.fixed_sessions = []

    def generate(self):
        ss = []
        fixed_time_assigned = 0.
        i = 1
        while(fixed_time_assigned < self.fixed_time):
            s = self.generate_session(i, "Fixed", self.fixed_type)
            self.generate_fixed(s)
            s.save()
            fixed_time_assigned += \
                first(first(s.window_set.all()).opportunity_set.all()).duration
            i += 1
            ss.append(s)

        windowed_time_assigned = 0.
        i = 1
        while(windowed_time_assigned < self.windowed_time):
            s = self.generate_session(i, "Windowed", self.windowed_type)
            self.generate_windowed(s)
            s.save()
            windowed_time_assigned += s.min_duration
            i += 1
            ss.append(s)
        return ss

    def generate_windowed(self, s):
        interval_period = choice(
                     self.windowed_interval_period_distribution)
        first_month = trimesterMonth.index(semester, 1)
        day         = randint(1, 28)

        first_day  = randint(2, 28)
        start_date = datetime(self.year, first_month, first_day)
        end_date   = datetime(self.year, first_month, 1) + \
                                                    timedelta(days = 90)
        while start_date < end_date:
            w = Window(session = s, required = True)
            w.save()
            o = Opportunity(window     = w
                          , start_time = start_date
                          , duration   = interval_period[1] * 24.
                            )
            o.save()
            start_date += timedelta(days = interval_period[0])

    
    def generate_fixed(self, s):
        first_month = trimesterMonth.index(semester, 1)
        day         = randint(1, 28)
        month = randint(first_month, first_month + 3) % 12 + 1
        hour  = randint(0, 23)
        dt    = datetime(self.year, month, day, hour)
        count = 0
        while self.overlap((dt, s.allotment.total_time)) or \
              self.below_horizon(s, dt):
            month = randint(first_month, first_month + 3) % 12 + 1
            hour  = randint(0, 23)
            dt    = datetime(self.year, month, day, hour)
            count += 1
            if count > 5:
                _, dec = s.get_ra_dec()
                dec += 5
                s.set_dec(dec)
                count = 0
        w = Window(session = s, required = True)
        w.save()
        o = Opportunity(window     = w
                      , start_time = dt
                      , duration   = s.allotment.total_time)
        o.save()
        self.fixed_sessions.append((dt, s.allotment.total_time))

    def generate_session(self, i, name, session_type):
        total_time = choice(total_time_dist)
        band       = choice(self.bands[semester])
        freq       = 2.0 if not self.frequencies.has_key(band) \
                         else self.frequencies.get(band)()
        s = Sesshun(project        = self.project
                  , session_type   = session_type
                  , observing_type = self.observing_type
                  , name           = "%s %i" % (name, i)
                  , frequency      = freq
                  , max_duration   = total_time
                  , min_duration   = total_time
                  , time_between   = choice(between_dist)
                  , grade          = choice(grade_dist)
                    )
        allot = Allotment(psc_time          = total_time
                        , total_time        = total_time
                        , max_semester_time = total_time
                        , grade             = s.grade
                          )
        allot.save()
        s.allotment = allot
        s.save()

        rcvr_name = self.deriveReceiver(s.frequency)
        rcvr   = first(Receiver.objects.filter(name = rcvr_name).all()
                     , Receiver.objects.all()[0])
        rg     = Receiver_Group(session = s)
        rg.save()
        rg.receiver_group_receiver_set.add(rcvr)
        rg.save()
        
        status = Status(session    = s
                      , enabled    = True
                      , authorized = True
                      , complete   = False
                      , backup     = False
                        )
        status.save()

        self.generate_target(s)
        s.save()
        return s

    def generate_target(self, s):
        # all sky or extra-galactic
        ra  = uniform(0.0, 23.999)
        dec = TimeAgent.rad2deg(
            asin(uniform(
                sin(TimeAgent.deg2rad(-35.0)), sin(TimeAgent.deg2rad(90.0))
                        ))
                                     )

        # galactic
        if choice(self.sky_types) == 'g':
            if random() < self.galactic_center_proportion:
                # galactic center
                ra  = 18.0
                dec = uniform(-27.0, -29.0)
            else:
                longitude   = uniform(0.0, 250.0)
                [rar, decr] = slalib.sla_galeq(
                                         TimeAgent.deg2rad(longitude), 0.0)
                ra  = TimeAgent.rad2hr(rar)
                dec = TimeAgent.rad2deg(decr)

        system = first(System.objects.filter(name = "J2000").all()
                     , System.objects.all()[0])
        target = Target(session    = s
                      , system     = system
                      , source     = "generated source"
                      , vertical   = ra
                      , horizontal = dec
                        )
        target.save()

    def below_horizon(self, s, starttime):
        endtime = starttime + timedelta(hours = s.allotment.total_time)
        return s.zenithAngle(starttime) > 85 or \
               s.zenithAngle(endtime) > 85

    def deriveReceiver(self, frequency):
        frequencies = [
              (.012,  "Rcvr_RRI")
            , (.395,  "Rcvr_342")
            , (.52,   "Rcvr_450")
            , (.69,   "Rcvr_600")
            , (.92,   "Rcvr_800")
            , (1.23,  "Rcvr_1070")
            , (1.73,  "Rcvr1_2")
            , (3.275, "Rcvr2_3")
            , (6.925, "Rcvr4_6")
            , (11.0,  "Rcvr8_10")
            , (16.7,  "Rcvr12_18")
            , (22.0,  "Rcvr18_22")
            , (26.25, "Rcvr22_26")
            , (40.5,  "Rcvr26_40")
            , (52.0,  "Rcvr40_52")
            ]

        receiver_name = 'NoiseSource'
        for freq, name in frequencies:
            if frequency <= freq:
                receiver_name = name
                break

        if 87.0 <= frequency <= 91.0:
            receiver_name = 'Rcvr_PAR'

        return receiver_name

    def overlap(self, oppt):
        endtime = oppt[0] + timedelta(hours = oppt[1])
        starttime = oppt[0]
        for o in self.fixed_sessions:
            scheduled_endtime = o[0] + timedelta(hours = o[1])
            scheduled_starttime = o[0]
            if scheduled_starttime <= starttime <  scheduled_endtime or \
               scheduled_starttime <  endtime   <= scheduled_endtime:
                return True
        return False

if __name__ == "__main__":
    g = Generate((0.45, 0.15, 0.4), 2920)
