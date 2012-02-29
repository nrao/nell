Ext.define('PHT.view.dashboard.Dashboard', {
    extend: 'Ext.tab.Panel',
    alias : 'widget.dashboard',
    title: 'Dashboard',

    
    items: [
      { title: "Import Reports",
        xtype: 'importreports',
      },
    ],

});
