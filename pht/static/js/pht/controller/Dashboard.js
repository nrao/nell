Ext.define('PHT.controller.Dashboard', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'ImportReport',
    ],

    stores: [
        'ImportReports',
    ],

    views: [
        'dashboard.Dashboard',
        'dashboard.ImportReports',
    ],

    init: function() {
        this.callParent(arguments);

    },

    notify: function(data) {
        if (data['notification'] == 'newImport') {
            // make sure the entire dashboard is expanded
            var south = Ext.getCmp('south-region');
            south.expand();
            // TBF: make sure this tab is selected
            // now make sure we load the most recent report
            var store = this.getImportReportsStore()
            store.load({
                scope   : this,
                callback: function(records, operation, success) {
                    var dt = records[0].get('create_date');
                    var r = records[0].get('report');
                    var importReports = south.down('panel');
                    importReports.reportDates.setValue(dt);
                    importReports.reportText.setValue(r);
                }            
            });
        }
    },

});    
