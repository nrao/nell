Ext.define('PHT.view.session.ListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.sessionlistwindow',
    title: 'Session Explorer',
    constrain: true,
    layout: 'fit',
    width: '60%',
    height: '45%',
    minWidth: 500,
    minHeight: 300,
    plain: true,
    //minimizable: true, //TBF: Doesn't work?!
    maximizable: true,
    items: {
        border: false
    },

    initComponent: function() {
        this.items =[{ xtype: 'sessionlist'}];
        this.callParent(arguments);
    },

    close: function() {
        this.hide();
    }
});
