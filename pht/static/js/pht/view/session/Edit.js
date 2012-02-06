Ext.define('PHT.view.session.Edit', {
    extend: 'Ext.window.Window',
    alias : 'widget.sessionedit',

    title : 'Edit Session',
    layout: 'fit',
    autoShow: true,
    constrain: true,

    initComponent: function() {

        this.items = [{xtype: 'sessionform'}];

        this.buttons = [
            {
                text: 'Save',
                action: 'save'
            },
            {
                text: 'Close',
                scope: this,
                handler: this.close
            },
            {
                text: 'Sources',
                action: 'sources'
            },
        ];

        this.callParent(arguments);

        
    },
});    

