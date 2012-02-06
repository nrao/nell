Ext.define('PHT.view.proposal.ListWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.proposallistwindow',
    title: 'Proposal Explorer',
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
        this.items =[{ xtype: 'proposallist'}];
        this.callParent(arguments);
    },

    close: function() {
        this.hide();
    }
});
