Ext.define('PHT.view.proposal.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.proposalform',
    trackResetOnLoad: true,
    initComponent: function() {
        // we want this event to bubble up to parents
        this.enableBubble('dirtychange');
        this.callParent(arguments);
    },
});
