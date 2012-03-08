Ext.define('PHT.view.session.ListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.sessionlistwindow',
    title: 'Session Explorer',
    constrain: true,
    layout: 'fit',
    width: '60%',
    height: '70%',
    plain: true,
    maximizable: true,
    x: 0,
    y: 300,
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
