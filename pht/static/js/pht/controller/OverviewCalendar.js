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
        'period.Edit',
        'period.List',
    ],

    init: function() {

        this.control({
            'overviewcalendar toolbar button[action=update]': {
                click: this.drawCalendar
            },
            'periodedit button[action=save]': {
                click: this.updatePeriod
            },            
            'periodlist' : {
                itemclick: this.highlightPeriod
            },
            
        });        

        this.callParent(arguments);
    },

    setOverviewCalendarWindow: function(ocWin) {
        this.oc = ocWin.getCalendar();
        this.pe = ocWin.getPeriodExplorer();
        this.drawCalendar();
    },

    highlightPeriod: function() {
        this.oc.highlight(this.pe.getSelectionModel().getSelection());
    },

    drawCalendar: function(){
        this.oc.removeAll(true);
        var numDays       = parseInt(this.oc.numDaysCombo.getValue());
        var drawComponent = this.oc.genDrawComponent(numDays);
        this.insertPeriods(drawComponent, numDays);
        this.oc.add(drawComponent);
        this.oc.doLayout();
    },

    insertPeriods: function(drawComponent, numDays) {
        var dssStore   = this.getStore('DssPeriods');
        var phtStore   = this.getStore('Periods');
        var me = this;

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
                dssStore.getProxy().extraParams = {startPeriods : startFmted,
                                                   daysPeriods  : numDays};

                dssStore.load({
                    scope: this,
                    callback: function(records, operation, success) {
                        var dayIndex;
                        var rxes;
                        var rcvrs;

                        // initialize the receivers needed by day
                        var rcvrDays = {};
                        for (i=0; i <= numDays; i++){
                            rcvrDays[i] = {};
                        }
                    
                        this.oc.removeAll(true);
                        var drawComponent = this.oc.genDrawComponent(numDays);

                        // draw the pht periods and parse rcvr info
                        for (p in phtPeriods) {
                            if (phtPeriods[p].get('dss_session_id') == null){
                                dayIndex = this.insertPeriod(phtPeriods[p], startDate, numDays, drawComponent, 'pht');
                                // TBF: we need to filter these periods by date,
                                // instead of getting them ALL and checking this.
                                if (dayIndex != -1) {
                                    rcvrs = this.getPhtPeriodReceivers(phtPeriods[p]);
                                    for (j in rcvrs){
                                        rcvrDays[dayIndex][rcvrs[j]] = 1;
                                    }
                                }
                            }
                        }

                        // draw the dss periods and parse rcvr info
                        for (r in records) {
                            dayIndex = this.insertPeriod(records[r], startDate, numDays, drawComponent, 'dss');
                            // In theory this shouldn't happen because we
                            // are filtering DSS periods on server side
                            if (dayIndex != -1) {
                                rcvrs = this.getDssPeriodReceivers(records[r]);
                                for (j in rcvrs){
                                    rcvrDays[dayIndex][rcvrs[j]] = 1;
                                }
                            }
                        }

                        // draw the receivers column
                        for (dayI in rcvrDays){
                            rcvrStr = "";
                            if (dayI > 0 ) {
                                for (rx in rcvrDays[dayI]){
                                    rcvrStr = rcvrStr + " " + rx;
                                }
                                this.oc.addRcvrList(drawComponent, dayI, rcvrStr);
                            }
                        }

                        Ext.Ajax.request({
                            url: '/pht/calendar/lstrange',
                            params: {
                                start:   startFmted,
                                numDays: numDays,
                            },
                            method: 'GET',
                            success: function(response) {
                                var endY     = 10 + numDays * me.oc.dayPx;
                                var json     = eval('(' + response.responseText + ')');
                                for(i in json.lines) {
                                    var pStartDate = me.getDssPeriodDate(json.lines[i].start.split(' ')[0]);
                                    var pEndDate   = me.getDssPeriodDate(json.lines[i].end.split(' ')[0]);
                                    var startIndex = 1 + (pStartDate - startDate) / 86400000;
                                    var endIndex   = 1 + (pEndDate - startDate) / 86400000;
                                    var startStr = json.lines[i].start.split(' ')[1].split(':');
                                    var endStr   = json.lines[i].end.split(' ')[1].split(':');
                                    var lstHrBegin = 
                                        parseFloat(startStr[0]) + (parseFloat(startStr[1]) / 60);
                                    var beginPx  = me.oc.px2time.time2px(lstHrBegin);
                                    var lstHrEnd = parseFloat(endStr[0]) + (parseFloat(endStr[1]) / 60);
                                    var endPx    = me.oc.px2time.time2px(lstHrEnd);
                                    var sDayPx   = me.oc.px2time.day2px(startIndex);
                                    var eDayPx   = me.oc.px2time.day2px(endIndex);
                                    var path     = ['M' + beginPx + ' ' + sDayPx
                                                  , 'L' + endPx + ' ' + eDayPx];
                                    if (i == 0 | (startIndex != 1 & i == 1)) {
                                        var color = 'red';
                                    } else {
                                        var color = 'gray';
                                    }
                                    drawComponent.items.push({
                                        type: 'path',
                                        stroke: color,
                                        path: path,
                                    });
                                }
                                me.oc.add(drawComponent);
                                me.oc.doLayout();
                            },
                        });

                    }
                });
            }
        });

    },

    updatePeriod: function(button) {
        this.selectedPeriods = [];                  
        this.updateRecord(button
                        , this.selectedPeriods
                        , this.getDssPeriodsStore()
                         );
    },

    // PHT periods simply have a comma separated list of receivers
    getPhtPeriodReceivers: function(period) {
        rxes = period.get('session_json').receivers;
        return rxes.split(',');
    },    
    
    // DSS periods use a logical expression for the receivers
    getDssPeriodReceivers: function(period) {
        var rcvrs = [];
        rxes = period.get('session').receiver;
        while(rxes.match('\\)') != null | rxes.match('\\(') != null | rxes.match(' ') != null) {
            rxes =rxes.replace(')', '');
            rxes =rxes.replace('(', '');
            rxes =rxes.replace(' ', '');
        } 
        rxes_ors = rxes.split('|');
        for (i in rxes_ors) {
            rxes_ands = rxes_ors[i].split('&');
            rcvrs = rcvrs.concat(rxes_ands);
        }
        return rcvrs;                        
    },

    getDssPeriodDate: function(dateStr) {
        dateStr = dateStr.split('-');
        periodDate = new Date();
        // Set the day first to avoid illegal dates like Feb 31st.
        periodDate.setUTCDate(dateStr[2]);
        periodDate.setUTCFullYear(dateStr[0]);
        periodDate.setUTCMonth(dateStr[1] - 1);
        // set the date again to avoid this whole illegal date nonsense.
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
        // Set the day first to avoid illegal dates like Feb 31st.
        periodDate.setUTCDate(dateStr[1]);
        periodDate.setUTCFullYear(dateStr[2]);
        periodDate.setUTCMonth(dateStr[0] - 1);
        // set the date again to avoid this whole illegal date nonsense.
        periodDate.setUTCDate(dateStr[1]);
        periodDate.setUTCHours(0);
        periodDate.setUTCMinutes(0);
        periodDate.setUTCSeconds(0);
        periodDate.setUTCMilliseconds(0);
        return periodDate
    },

    insertPeriod: function(record, startDate, numDays, drawComponent, pType) {
        var period;
        var periodDate;
        var dayIndex;
        var timeStr;
        var time;
        var rxes;
        var receivers;
        period  = Ext.create('PHT.view.overview.Period');
        var dateStr = record.get('date')
        // DSS and PHT periods are ALMOST identical
        if (pType == 'dss') {
            periodDate = this.getDssPeriodDate(dateStr);
            receivers = record.get('session').receiver
        } else {
            periodDate = this.getPhtPeriodDate(dateStr);
            receivers = record.get('session_json').receivers
        }
        timeStr = record.get('time').split(':');
        time    = parseFloat(timeStr[0]) + (parseFloat(timeStr[1]) / 60);
        dayIndex = 1 + (periodDate - startDate) / 86400000;
        // safegaurd that this period lands on our calendar
        if (dayIndex > numDays | dayIndex < 0) {
            return -1;
        } else {    
            period.setDrawComponent(drawComponent);
            period.setDay(dayIndex);
            period.setTime(time, parseFloat(record.get('duration')));
            period.setData(record, pType, receivers);
            this.oc.addPeriod(period);
            return dayIndex
        }    
    },    
});
