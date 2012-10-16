Ext.define('PHT.view.proposal.SemesterSomethingForm', {
    extend: 'Ext.window.Window',
    alias : 'widget.proposalsemestersomethingform',
    title : 'Semester Something',
    layout: 'fit',
    autoShow: true,
    plain: true,
    width: 400,
    height: 225,
    additionalItems: [],

    initComponent: function() {
        var formItems = [
                    {
                        xtype: 'combo',
                        name: 'semester',
                        fieldLabel: 'Semester',
                        store: 'Semesters',
                        queryMode: 'local',
                        displayField: 'semester',
                        valueField: 'semester',
                    },
                    
                ];
        formItems = formItems.concat(this.additionalItems);
        this.items = [
            {
                xtype: 'form',
                items: formItems,
            },
        ];

        this.buttons = [{
                text: 'Submit',
                action: 'submit'
            },{
                text: 'Cancel',
                scope: this,
                handler: this.close,
            },
        ];

        this.callParent(arguments);
    },
});
