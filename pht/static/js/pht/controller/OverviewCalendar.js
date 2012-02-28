Ext.define('PHT.controller.OverviewCalendar', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'DssPeriod',
        'Period',
    ],

    stores: [
        'DssPeriods',
        'Periods',
    ],

    views: [
        'overview.Calendar',
    ],

    init: function() {

        this.control({
            'overviewcalendar toolbar button[action=update]': {
                click: this.drawCalendar
            },
            
        });        

        this.callParent(arguments);
    },

    setOverviewCalendar: function(oc) {
        this.oc = oc;
        this.drawCalendar();
    },

    drawCalendar: function(){
        this.oc.removeAll(true);
        var numDays       = this.oc.numDaysCombo.getValue();
        var drawComponent = this.oc.genDrawComponent(numDays);
        this.insertPeriods(drawComponent, numDays);
        this.oc.add(drawComponent);
        this.oc.doLayout();
    },

    insertPeriods: function(drawComponent, numDays) {
        var dssStore   = this.getStore('DssPeriods');
        var phtStore   = this.getStore('Periods');

        // What's the start date (at midnight) of our calendar?
        var start      = this.oc.startDateField.getValue();
        var startDate  = new Date();
        startDate.setUTCFullYear(start.getUTCFullYear());
        startDate.setUTCMonth(start.getUTCMonth());
        startDate.setUTCDate(start.getUTCDate());
        startDate.setUTCHours(0);
        startDate.setUTCMinutes(0);
        startDate.setUTCSeconds(0);
        startDate.setUTCMilliseconds(0);

        // first get the pht periods
        phtStore.load({
            scope: this,
            callback: function(records, operation, success) {

                var phtPeriods = records;

                // now get the dss periods
                var startFmted = startDate.getUTCFullYear() + '-' + (startDate.getUTCMonth()+1) + '-' + startDate.getUTCDate();
                var url = '/scheduler/periods/UTC?startPeriods=' + startFmted+ '&daysPeriods=' + numDays;
                dssStore.getProxy().url = url;
                dssStore.load({
                    scope: this,
                    callback: function(records, operation, success) {


                        var dayIndex;
                        var rxes;
                        var rcvrDays = {};
                        for (i=0; i <= numDays; i++){
                            rcvrDays[i] = {};
                        }
                    
                        this.oc.removeAll(true);
                        var drawComponent = this.oc.genDrawComponent(numDays);

                        for (p in phtPeriods) {
                            dayIndex = this.insertPeriod(phtPeriods[p], startDate, numDays, drawComponent, 'pht');
                            console.log(phtPeriods[p]);
                            rxes = phtPeriods[p].get('session_json').receivers;
                            console.log(rxes);
                            rxes_ands = rxes.split(',');
                            for (j in rxes_ands){
                                rcvrDays[dayIndex][rxes_ands[j]] = 1;
                            }
                            console.log(rcvrDays);
                            /*
                            for (dayI in rcvrDays){
                                rcvrStr = "";
                                if (dayI > 0 ) {
                                    for (rx in rcvrDays[dayI]){
                                        rcvrStr = rcvrStr + " " + rx;
                                    }
                                    this.oc.addRcvrList(drawComponent, dayI, rcvrStr);
                                }
                            }
                            */
                        }
                        for (r in records) {
                            console.log("inserting this period next: ");
                            console.log(r);
                            console.log(records[r]);

                            dayIndex = this.insertPeriod(records[r], startDate, numDays, drawComponent, 'dss');

                            rxes = records[r].get('session').receiver;
                            console.log(rxes)
                            while(rxes.match('\\)') != null | rxes.match('\\(') != null | rxes.match(' ') != null) {
                                rxes =rxes.replace(')', '');
                                rxes =rxes.replace('(', '');
                                rxes =rxes.replace(' ', '');
                            } 
                            rxes_ors = rxes.split('|');
                            for (i in rxes_ors) {
                                rxes_ands = rxes_ors[i].split('&');
                                for (j in rxes_ands){
                                    rcvrDays[dayIndex][rxes_ands[j]] = 1;
                                }
                            }
                            console.log(rcvrDays);
                            /*
                            for (dayI in rcvrDays){
                                rcvrStr = "";
                                if (dayI > 0 ) {
                                    for (rx in rcvrDays[dayI]){
                                        rcvrStr = rcvrStr + " " + rx;
                                    }
                                    this.oc.addRcvrList(drawComponent, dayI, rcvrStr);
                                }
                            }
                            */
                        }

                        for (dayI in rcvrDays){
                            rcvrStr = "";
                            if (dayI > 0 ) {
                                for (rx in rcvrDays[dayI]){
                                    rcvrStr = rcvrStr + " " + rx;
                                }
                                this.oc.addRcvrList(drawComponent, dayI, rcvrStr);
                            }
                        }

                        console.log("DONE!");
                        this.oc.add(drawComponent);
                        this.oc.doLayout();
                    }
                });    
            }
        });

    },

    getDssPeriodDate: function(dateStr) {
        dateStr = dateStr.split('-');
        periodDate = new Date();
        periodDate.setUTCFullYear(dateStr[0]);
        periodDate.setUTCMonth(dateStr[1] - 1);
        periodDate.setUTCDate(dateStr[2]);
        periodDate.setUTCHours(0);
        periodDate.setUTCMinutes(0);
        periodDate.setUTCSeconds(0);
        periodDate.setUTCMilliseconds(0);
        return periodDate
    },

    getPhtPeriodDate: function(dateStr) {
        dateStr = dateStr.split('/');
        periodDate = new Date();
        periodDate.setUTCFullYear(dateStr[2]);
        periodDate.setUTCMonth(dateStr[0] - 1);
        periodDate.setUTCDate(dateStr[1]);
        periodDate.setUTCHours(0);
        periodDate.setUTCMinutes(0);
        periodDate.setUTCSeconds(0);
        periodDate.setUTCMilliseconds(0);
        return periodDate
    },

    insertPeriod: function(record, startDate, numDays, drawComponent, type) {
        console.log('insertPeriod: ' + type);
        console.log(record);
        var period;
        var periodDate;
        var dayIndex;
        var timeStr;
        var time;
        var rxes;
        var receivers;
        period  = Ext.create('PHT.view.overview.Period');
        //period.setPeriodType(type)
        var dateStr = record.get('date')
        // deal with the two different date formats
        //if (dateStr.search('-') != -1) {
        if (type == 'dss') {
            periodDate = this.getDssPeriodDate(dateStr);
            receivers = record.get('session').receiver
        } else {
            periodDate = this.getPhtPeriodDate(dateStr);
            receivers = record.get('session_json').receivers
        }
        timeStr = record.get('time').split(':');
        time    = parseFloat(timeStr[0]) + (parseFloat(timeStr[1]) / 60);
        dayIndex = 1 + (periodDate - startDate) / 86400000;
        period.setDrawComponent(drawComponent);
        //period.setColor('#'+'0123456789abcdef'.split('').map(function(v,i,a){
        //  return i>5 ? null : a[Math.floor(Math.random()*16)] }).join(''));
        period.setDay(dayIndex);
        period.setTime(time, parseFloat(record.get('duration')));
        period.setData(record, type, receivers);
        return dayIndex
    },    

});
