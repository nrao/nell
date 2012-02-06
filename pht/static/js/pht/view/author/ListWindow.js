Ext.define('PHT.view.author.ListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.authorlistwindow',
    title: 'Proposal Authors',
    constrain: true,
    layout: 'fit',
    width: '95%',
    height: '45%',
    minWidth: 500,
    minHeight: 300,
    plain: true,
    items: {
        border: false
    },

    initComponent: function() {
        this.items =[{ xtype: 'authorlist'}];
        this.callParent(arguments);
    },

    close: function() {
        this.hide();
    }
});
