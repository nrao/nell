Ext.define('PHT.view.session.Edit', {
    extend: 'PHT.view.Edit',
    alias : 'widget.sessionedit',
    title : 'Edit Session',

    initComponent: function() {

        this.items = [
            {
                xtype: 'sessionform',
                trackResetOnLoad: true,
            }
        ];

        // Add these to the Save & Close buttons
        this.buttons = [
            {
                text: 'Sources',
                action: 'sources'
            },
        ];

        this.callParent(arguments);
        
    },
});    

