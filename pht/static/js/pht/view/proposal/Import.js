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
            title: 'Reimport Proposal(s)',
            defaultType: 'textfield',
            collapsible: true,
            checkboxToggle: true,
            checkboxName: 'proposalsCheckbox',
            layout: 'anchor',
            listeners: {
                expand: function() {
                    semester.collapse();
                    pstProposals.collapse();
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
                    pstProposals.collapse();
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
                 {
                    xtype: 'checkbox',
                    fieldLabel: 'Just import SRP scores',
                    name: 'srp',
                    id: 'srp',
                    uncheckedValue: 'false',
                    inputValue: 'true',
                    value: 'true',
                    labelStyle: '',
                 },
            ]
        });

        var pstProposals = Ext.create('PHT.view.proposal.PhtFieldSet', {
            title: 'Import PST Proposal(s)',
            defaultType: 'textfield',
            collapsible: true,
            checkboxToggle: true,
            checkboxName: 'pstProposalsCheckbox',
            layout: 'anchor',
            collapsed: true,
            listeners: {
                expand: function() {
                    semester.collapse();
                    proposals.collapse();
                }
            },
            items: [
                {
                    xtype: 'combo',
                    name: 'pcode',
                    fieldLabel: 'PST PCODE',
                    store: 'PstProposalCodes', 
                    queryMode: 'local',
                    displayField: 'pcode',
                    valueField: 'pcode',
                    multiSelect: true,
                },
            ]
        });

        this.items = [
            {
                xtype: 'form',
                items: [
                    proposals,
                    semester,
                    pstProposals,
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
