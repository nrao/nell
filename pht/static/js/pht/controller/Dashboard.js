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

});    
