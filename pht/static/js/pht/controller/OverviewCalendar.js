Ext.define('PHT.controller.OverviewCalendar', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'DssPeriod',
    ],

    stores: [
        'DssPeriods',
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
        var start      = this.oc.startDateField.getValue();
        var startDate  = new Date();
        startDate.setUTCFullYear(start.getUTCFullYear());
        startDate.setUTCMonth(start.getUTCMonth());
        startDate.setUTCDate(start.getUTCDate());
        startDate.setUTCHours(0);
        startDate.setUTCMinutes(0);
        startDate.setUTCSeconds(0);
        startDate.setUTCMilliseconds(0);

        var startFmted = startDate.getUTCFullYear() + '-' + (startDate.getUTCMonth()+1) + '-' + startDate.getUTCDate();
        var url = '/scheduler/periods/UTC?startPeriods=' + startFmted+ '&daysPeriods=' + numDays;
        dssStore.getProxy().url = url;
        dssStore.load({
            scope: this,
            callback: function(records, operation, success) {
                this.oc.removeAll(true);
                var drawComponent = this.oc.genDrawComponent(numDays);
                var period;
                var periodDate;
                var dayIndex;
                var timeStr;
                var time;
                var rxes;
                var rcvrDays = {};
                for (i=0; i <= numDays; i++){
                    rcvrDays[i] = {};
                }

                for (r in records) {
                    dateStr = records[r].get('date').split('-');
                    timeStr = records[r].get('time').split(':');
                    time    = parseFloat(timeStr[0]) + (parseFloat(timeStr[1]) / 60);
                    periodDate = new Date();
                    periodDate.setUTCFullYear(dateStr[0]);
                    periodDate.setUTCMonth(dateStr[1] - 1);
                    periodDate.setUTCDate(dateStr[2]);
                    periodDate.setUTCHours(0);
                    periodDate.setUTCMinutes(0);
                    periodDate.setUTCSeconds(0);
                    periodDate.setUTCMilliseconds(0);
                    dayIndex = 1 + (periodDate - startDate) / 86400000;

                    period  = Ext.create('PHT.view.overview.Period');
                    period.setDrawComponent(drawComponent);
                    period.setColor('#'+'0123456789abcdef'.split('').map(function(v,i,a){
                      return i>5 ? null : a[Math.floor(Math.random()*16)] }).join(''));
                    period.setDay(dayIndex);
                    period.setTime(time, parseFloat(records[r].get('duration')));
                    period.setData(records[r]);

                    rxes = records[r].get('session').receiver;
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

                this.oc.add(drawComponent);
                this.oc.doLayout();
            }
        });

    },


});
