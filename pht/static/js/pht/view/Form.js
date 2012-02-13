Ext.define('PHT.view.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.phtform',
    trackResetOnLoad: true,
    initComponent: function() {
        // we want this event to bubble up to parents
        this.enableBubble('dirtychange');
        this.callParent(arguments);
    },
});
