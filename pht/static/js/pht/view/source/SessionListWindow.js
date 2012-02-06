Ext.define('PHT.view.source.SessionListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.sessionsourcelistwindow',
    title: 'Session Sources',
    constrain: true,
    layout: 'fit',
    width: '60%',
    height: '45%',
    minWidth: 500,
    minHeight: 300,
    plain: true,
    x: 20,
    y: 20,
    items: {
        border: false
    },

    initComponent: function() {
        this.items =[{ xtype: 'sessionsourcelist'}];
        this.callParent(arguments);
    },

    close: function() {
        this.hide();
    }
});
