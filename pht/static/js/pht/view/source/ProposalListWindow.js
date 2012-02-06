Ext.define('PHT.view.source.ProposalListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.proposalsourcelistwindow',
    title: 'Proposal Sources',
    constrain: true,
    layout: 'fit',
    width: '60%',
    height: '45%',
    minWidth: 500,
    minHeight: 300,
    plain: true,
    x: 5,
    y: 5,
    items: {
        border: false
    },

    initComponent: function() {
        this.items =[{ xtype: 'proposalsourcelist'}];
        this.callParent(arguments);
    },

    close: function() {
        this.hide();
    }
});
