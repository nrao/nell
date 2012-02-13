Ext.define('PHT.view.proposal.Import', {
    extend: 'Ext.window.Window',
    alias : 'widget.proposalimport',

    title : 'Import Proposal(s)',
    layout: 'fit',
    autoShow: true,
    plain: true,
    width: 400,
    height: 200,
    //constrain: true,

    initComponent: function() {
        var proposals = Ext.create('PHT.view.proposal.PhtFieldSet', {
            title: 'Import Proposal(s)',
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
                    store: 'ProposalCodes', 
                    queryMode: 'local',
                    displayField: 'pcode',
                    valueField: 'pcode',
                    multiSelect: true,
                },
            ]
        });
        var semester = Ext.create('PHT.view.proposal.PhtFieldSet', {
            title: 'Import Semester',
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
        this.items = [
            {
                xtype: 'form',
                items: [
                    proposals,
                    semester
                ]
            },
        ];

        this.buttons = [
            {
                text: 'Import',
                action: 'import'
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
