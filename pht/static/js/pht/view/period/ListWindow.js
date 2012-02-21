Ext.define('PHT.view.period.ListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.periodlistwindow',
    title: 'Period Explorer',
    constrain: true,
    layout: 'fit',
    width: '90%',
    height: '90%',
    minWidth: 500,
    minHeight: 300,
    plain: true,
    //minimizable: true, //TBF: Doesn't work?!
    maximizable: true,
    items: {
        border: false
    },

    initComponent: function() {
        this.items =[{ xtype: 'periodlist'}];
        this.callParent(arguments);
    },

    close: function() {
        this.hide();
    }
});
