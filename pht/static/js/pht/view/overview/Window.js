Ext.define('PHT.view.overview.Window', {
    extend: 'Ext.window.Window',
    alias: 'widget.overviewcalendarwindow',
    autoScroll: true,
    width: '90%',
    height: '90%',
    layout: 'border',
    constrainHeader: true,
    title: 'Overview Calendar',
    maximizable: true,
    autoshow: true,

    items: [
        {
            region: 'center',
            xtype: 'overviewcalendar',
            layout: 'fit',
        }, {
            title: 'Period Explorer',
            region: 'south',
            xtype: 'periodlist',
            height: '25%',
            cmargins: '5 0 0 0',
        },
    ],

    getCalendar: function() {
        return this.down('overviewcalendar');
    },

    getPeriodExplorer: function() {
        return this.down('periodlist');
    },

    close: function() {
        this.hide();
    }
});


