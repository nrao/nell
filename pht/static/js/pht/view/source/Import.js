Ext.define('PHT.view.source.Import', {
    extend: 'Ext.window.Window', 
    alias : 'widget.sourceimport',
    title : 'Import Sources',
    layout: 'fit',
    autoShow: true,
    plain: true,

    initComponent: function() {
        this.items = [{
            xtype: 'form',
            trackResetOnLoad: true,

            items: [{
                xtype: 'filefield',
                width: 500,
                id: 'form-file',
                emptyText: 'Select a file.',
                fieldLabel: 'File',
                name: 'file',
                buttonText: 'Browse...',
            }],   
        }],
        this.buttons = [{
            text: 'Save',
            action: 'import',
        }]
        this.callParent(arguments);
    },
});

        

