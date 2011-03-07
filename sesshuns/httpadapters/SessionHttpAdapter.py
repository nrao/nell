from nell.utilities  import TimeAgent
from nell.tools      import TimeAccounting
from sesshuns.models import *

class SessionHttpAdapter (object):

    def __init__(self, sesshun):
        self.sesshun = sesshun

    def load(self, sesshun):
        self.sesshun = sesshun

    def set_base_fields(self, fdata):
        fsestype = fdata.get("type", "open")
        fobstype = fdata.get("science", "testing")
        proj_code = fdata.get("pcode", "GBT09A-001")

        p  = first(Project.objects.filter(pcode = proj_code).all()
                 , Project.objects.all()[0])
        st = first(Session_Type.objects.filter(type = fsestype).all()
                 , Session_Type.objects.all()[0])
        ot = first(Observing_Type.objects.filter(type = fobstype).all()
                 , Observing_Type.objects.all()[0])

        self.sesshun.project          = p
        self.sesshun.session_type     = st
        self.sesshun.observing_type   = ot
        self.sesshun.original_id      = \
            self.get_field(fdata, "orig_ID", None, lambda x: int(float(x)))
        self.sesshun.name             = fdata.get("name", None)
        self.sesshun.frequency        = fdata.get("freq", None)
        self.sesshun.max_duration     = TimeAgent.rndHr2Qtr(float(fdata.get("req_max", 12.0)))
        self.sesshun.min_duration     = TimeAgent.rndHr2Qtr(float(fdata.get("req_min",  3.0)))
        self.sesshun.time_between     = fdata.get("between", None)

    def get_field(self, fdata, key, defaultValue, cast):
        "Some values from the JSON dict we know we need to type cast"
        value = fdata.get(key, defaultValue)
        if cast != bool:
            return value if value is None else cast(value)
        else:
            return value == "true"

    def init_from_post(self, fdata):
        self.set_base_fields(fdata)

        allot = Allotment(psc_time          = fdata.get("PSC_time", 0.0)
                        , total_time        = fdata.get("total_time", 0.0)
                        , max_semester_time = fdata.get("sem_time", 0.0)
                        , grade             = fdata.get("grade", 4.0)
                          )
        allot.save()
        self.sesshun.allotment        = allot

        status = Status(
                   enabled    = self.get_field(fdata, "enabled", True, bool)
                 , authorized = self.get_field(fdata, "authorized", True, bool)
                 , complete   = self.get_field(fdata, "complete", True, bool) 
                 , backup     = self.get_field(fdata, "backup", True, bool) 
                        )
        status.save()
        self.sesshun.status = status
        self.sesshun.save()
        
        proposition = fdata.get("receiver")
        self.save_receivers(proposition)
        
        systemName = fdata.get("coord_mode", "J2000")
        system = first(System.objects.filter(name = systemName).all()
                     , System.objects.all()[0])

        v_axis = fdata.get("source_v", 0.0)
        h_axis = fdata.get("source_h", 0.0)
        
        target = Target(session    = self.sesshun
                      , system     = system
                      , source     = fdata.get("source", None)
                      , vertical   = v_axis
                      , horizontal = h_axis
                        )
        target.save()
        self.sesshun.save()

    def save_receivers(self, proposition):
        abbreviations = [r.abbreviation for r in Receiver.objects.all()]
        rc = ReceiverCompile(abbreviations)
        ands = rc.normalize(proposition)

        for ors in ands:
            rg = Receiver_Group(session = self.sesshun)
            rg.save()
            for rcvr in ors:
                rcvrId = Receiver.objects.filter(abbreviation = rcvr)[0]
                rg.receivers.add(rcvrId)
                rg.save()

    def update_from_post(self, fdata):
        self.set_base_fields(fdata)
        self.sesshun.save()

        self.sesshun.allotment.psc_time          = fdata.get("PSC_time", 0.0)
        self.sesshun.allotment.total_time        = fdata.get("total_time", 0.0)
        self.sesshun.allotment.max_semester_time = fdata.get("sem_time", 0.0)
        self.sesshun.allotment.grade             = fdata.get("grade", 4.0)
        self.sesshun.allotment.save()
        self.sesshun.save()

        self.sesshun.status.enabled    = self.get_field(fdata, "enabled", True, bool) 
        self.sesshun.status.authorized = self.get_field(fdata, "authorized", True, bool)
        self.sesshun.status.complete   = self.get_field(fdata, "complete", True, bool) 
        self.sesshun.status.backup     = self.get_field(fdata, "backup", True, bool) 
        self.sesshun.status.save()
        self.sesshun.save()

        self.update_bool_obs_param(fdata, "transit", "Transit", self.sesshun.transit())
        self.update_bool_obs_param(fdata, "nighttime", "Night-time Flag", \
            self.sesshun.nighttime())
        self.update_guaranteed(fdata)
        
        self.update_lst_exclusion(fdata)    
        self.update_xi_obs_param(fdata, self.sesshun.get_min_eff_tsys_factor())
        self.update_el_limit_obs_param(fdata
                                     , self.sesshun.get_elevation_limit())

        proposition = fdata.get("receiver", None)
        if proposition is not None:
            self.sesshun.receiver_group_set.all().delete()
            self.save_receivers(proposition)

        systemName = fdata.get("coord_mode", "J2000")
        system = first(System.objects.filter(name = systemName).all()
                     , System.objects.all()[0])

        v_axis = fdata.get("source_v", None)
        h_axis = fdata.get("source_h", None)

        t            = first(self.sesshun.target_set.all())
        t.system     = system
        t.source     = fdata.get("source", None)
        t.vertical   = v_axis if v_axis is not None else t.vertical
        t.horizontal = h_axis if h_axis is not None else t.horizontal
        t.save()

        self.sesshun.save()

    def update_parameter(self, fdata, old_value, new_value, parameter):
        if old_value is None:
            if new_value and new_value != 1.0:
                obs_param =  Observing_Parameter(session     = self.sesshun
                                               , parameter   = parameter
                                                )
                obs_param.setValue(new_value)
                obs_param.save()
        else:
            obs_param = self.sesshun.observing_parameter_set.filter(parameter=parameter)[0]
            if new_value and new_value != 1.0:
                obs_param.setValue(new_value)
            else:
                obs_param.delete()

    def update_xi_obs_param(self, fdata, old_value):
        """
        For taking a json dict and converting its given
        xi float field into a 'Min Eff TSys' float observing parameter.
        """
        self.update_parameter(fdata
                            , old_value
                            , self.get_field(fdata, "xi_factor", 1.0, float)
                            , first(Parameter.objects.filter(name="Min Eff TSys"))
                            )

    def update_el_limit_obs_param(self, fdata, old_value):
        """
        For taking a json dict and converting its given
        el limit float field into a 'El Limit' float observing parameter.
        """
        new_value = self.get_field(fdata, "el_limit", None, float)
        if new_value is not None: # make sure it's in a legal range
            try:
                fv = float(new_value)
                if fv < 5.0 or fv > 90.0:
                    return # value out of range
            except:
                return # nonsense value

        parameter = Parameter.objects.filter(name="El Limit")[0]
        self.update_parameter(fdata, old_value, new_value, parameter)

    def update_bool_obs_param(self, fdata, json_name, name, old_value):
        """
        Generic method for taking a json dict and converting its given
        boolean field into a boolean observing parameter.
        """

        new_value = self.get_field(fdata, json_name, False, bool)
        parameter = Parameter.objects.filter(name=name)[0]
        self.update_parameter(fdata, old_value, new_value, parameter)

    def update_guaranteed(self, fdata):
        """
        Interpreting the guaranteed flag in the JSON is tedious, because
        it is the opposite of the boolean Obs. Param. 'Not Guaranteed',
        and Obs. Param.'s are False if they are not there ...
        """
        # guaranteed
        guaranteed = fdata.get("guaranteed", "true") == "true"
        
        param = Parameter.objects.get(name = "Not Guaranteed")
        old_value = self.sesshun.not_guaranteed()
        if old_value is None:
            # The Obs. Param. hasn't been used it, so set it only if
            # the Obs. Param. will be True
            if not guaranteed:
                # session is not guaranteed, and we're setting this 
                # for the first time
                op = Observing_Parameter(session = self.sesshun
                                       , parameter = param
                                       , boolean_value = True
                                         )
                op.save()
        else:
            # The Obs. Param is already in use, so use it.
            op = self.sesshun.observing_parameter_set.filter(parameter=param)[0]
            if guaranteed:
                # Equivalent to 'Not Gaurenteed' == False
                op.delete()
            else:
                # Not Gaurenteed == True
                op.boolean_value = True
                op.save()

    def update_lst_exclusion(self, fdata):
        """
        Converts the json representation of the LST exclude flag
        to the model representation.
        """
        lowParam = first(Parameter.objects.filter(name="LST Exclude Low"))
        hiParam  = first(Parameter.objects.filter(name="LST Exclude Hi"))
        
        # json dict string representation
        lst_ex_string = fdata.get("lst_ex", None)
        if lst_ex_string:
            # unwrap and get the float values
            lowStr, highStr = lst_ex_string.split("-")
            low = float(lowStr)
            high = float(highStr)
            assert low <= high

        # get the model's string representation
        current_lst_ex_string = self.sesshun.get_LST_exclusion_string()

        if current_lst_ex_string == "":
            if lst_ex_string:
                # create a new LST Exlusion range
                obs_param =  Observing_Parameter(session = self.sesshun
                                               , parameter = lowParam
                                               , float_value = low 
                                                )
                obs_param.save()
                obs_param =  Observing_Parameter(session = self.sesshun
                                               , parameter = hiParam
                                               , float_value = high 
                                                )
                obs_param.save()
            else:
                # they are both none, nothing to do
                pass
        else:
            # get the current model representation (NOT the string) 
            lowObsParam = \
                first(self.sesshun.observing_parameter_set.filter(parameter=lowParam))
            highObsParam = \
                first(self.sesshun.observing_parameter_set.filter(parameter=hiParam))
            if lst_ex_string:
                lowObsParam.float_value = low
                lowObsParam.save()
                highObsParam.float_value = high
                highObsParam.save()
            else:
                lowObsParam.delete()
                highObsParam.delete()

    def jsondict(self):
        d = {"id"         : self.sesshun.id
           , "pcode"      : self.sesshun.project.pcode
           , "type"       : self.sesshun.session_type.type
           , "science"    : self.sesshun.observing_type.type
           , "total_time" : self.sesshun.allotment.total_time
           , "PSC_time"   : self.sesshun.allotment.psc_time
           , "sem_time"   : self.sesshun.allotment.max_semester_time
           , "remaining"  : 0 if self.sesshun.observing_type.type == "maintenance" \
                              else TimeAccounting().getTimeRemaining(self.sesshun)
           , "grade"      : self.sesshun.allotment.grade
           , "orig_ID"    : self.sesshun.original_id
           , "name"       : self.sesshun.name
           , "freq"       : self.sesshun.frequency
           , "req_max"    : self.sesshun.max_duration
           , "req_min"    : self.sesshun.min_duration
           , "between"    : self.sesshun.time_between
           , "enabled"    : self.sesshun.status.enabled
           , "authorized" : self.sesshun.status.authorized
           , "complete"   : self.sesshun.status.complete
           , "backup"     : self.sesshun.status.backup
           , "guaranteed" : self.sesshun.guaranteed()
           , "transit"    : self.sesshun.transit() or False
           , "nighttime"  : self.sesshun.nighttime() or False
           , "lst_ex"     : self.sesshun.get_LST_exclusion_string() or ""
           , "receiver"   : self.sesshun.get_receiver_req()
           , "project_complete" : "Yes" if self.sesshun.project.complete else "No"
           , "xi_factor"  : self.sesshun.get_min_eff_tsys_factor() or 1.0
           , "el_limit"   : self.sesshun.get_elevation_limit() or None # None is default 
            }

        target = first(self.sesshun.target_set.all())
        if target is not None:
            d.update({"source"     : target.source
                    , "coord_mode" : target.system.name
                    , "source_h"   : target.horizontal
                    , "source_v"   : target.vertical
                      })

        #  Remove all None values
        for k, v in d.items():
            if v is None:
                _ = d.pop(k)

        return d

