Ext.define('PHT.view.proposal.ListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.proposallistwindow',
    title: 'Proposal Explorer',
    constrain: true,
    layout: 'fit',
    width: '100%',
    height: '30%',
    plain: true,
    maximizable: true,
    x: 0,
    y: 0,
    items: {
        border: false
    },

    initComponent: function() {
        this.items =[{ xtype: 'proposallist'}];
        this.callParent(arguments);
    },

    close: function() {
        this.hide();
    }
});
