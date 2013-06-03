Ext.define('PHT.view.proposal.Export', {
    extend: 'Ext.window.Window',
    alias : 'widget.proposalexport',

    title : 'Transfer Proposal(s) to the DSS',
    layout: 'fit',
    autoShow: true,
    plain: true,
    width: 400,
    height: 225,
    //constrain: true,

    initComponent: function() {
        var proposals = Ext.create('PHT.view.proposal.PhtFieldSet', {
            title: 'Transfer Proposal(s)',
            defaultType: 'textfield',
            collapsible: true,
            checkboxToggle: true,
            checkboxName: 'proposalsCheckbox',
            layout: 'anchor',
            listeners: {
                expand: function() {
                    semester.collapse();
                }
            },
            items: [
                {
                    xtype: 'combo',
                    name: 'pcode',
                    fieldLabel: 'PCODE',
                    store: 'Proposals', 
                    queryMode: 'local',
                    displayField: 'pcode',
                    valueField: 'pcode',
                    multiSelect: true,
                },
            ]
        });
        var semester = Ext.create('PHT.view.proposal.PhtFieldSet', {
            title: 'Transfer Semester',
            defaultType: 'textfield',
            layout: 'anchor',
            collapsible: true,
            checkboxToggle: true,
            checkboxName: 'semesterCheckbox',
            collapsed: true,
            listeners: {
                expand: function() {
                    proposals.collapse();
                }
            },
            items: [
                {
                    xtype: 'combo',
                    name: 'semester',
                    fieldLabel: 'Semester',
                    store: 'Semesters',
                    queryMode: 'local',
                    displayField: 'semester',
                    valueField: 'semester',
                },
            ]
        });
        var astrid = Ext.create('Ext.form.field.Checkbox', {
                        fieldLabel: 'Add to Astrid',
                        name: 'astrid',
                        id: 'astrid',
                        uncheckedValue: 'false',
                        inputValue: 'true',
                        value: 'true',
                        labelStyle: '',
        });
        astrid.setValue(true);
        
        this.items = [
            {
                xtype: 'form',
                items: [
                    {
                        xtype: 'label',
                        forId: 'help',
                        text: 'Exported proposals will be avaliable in the DSS scheduling interface after the transfer.',
                    },
                    proposals,
                    semester,
                    astrid,
                ]
            },
        ];

        this.buttons = [
            {
                text: 'Transfer',
                action: 'export'
            },
            {
                text: 'Cancel',
                scope: this,
                handler: this.close,
            },
        ];

        this.callParent(arguments);
    },
});
