/*
We need to have the following comments accessible to the client: Technical reviews to TAC, (Same? TAC comments to PI, NRAO comments), SRP Science Review, Technical Review(s), SRP to TAC, TAC comments to NRAO (aka sched note).

The following should be editable in the GB PHT. TAC comments to PI, NRAO Comments, Technical Review(s), and TAC comments to NRAO.
*/

Ext.define('PHT.view.proposal.TacTool', {
    //extend: 'Ext.window.Window',
    extend: 'PHT.view.Edit',
    alias : 'widget.tactool',
    title : 'TAC Tool',
    autoscroll: true,
    layout: 'fit',
    height: '70%',
    x: 700,
    y: 225,
    initComponent: function() {
        var me = this;
        this.proposalCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'pcode',
            store: 'ProposalCodes',
            queryMode: 'local',
            displayField: 'pcode',
            valueField: 'pcode',
            hideLabel: true,
            emptyText: 'Select a proposal...',
            listeners: {
                select: function(combo, record, index) {
                    var pcode = record[0].get('pcode');
                    me.setProposalByPcode(pcode);
                }
            },
        });

        this.allocateBtn = Ext.create('Ext.button.Button', {
            text: 'Allocate',
            action: 'allocate',
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,        
                { xtype: 'tbseparator'},
                this.allocateBtn,
            ]},
        ];

        this.items = [{
            xtype: 'phtform',
            autoScroll: true,
            border: false,
            trackResetOnLoad: true,
            fieldDefaults: {
               labelStyle: 'font-weight:bold',
            },
            defaults: {
                width: 500,
                height: 100,
                allowBlank: true,
                labelStyle: '',    
            },
            items: [{
                xtype: 'textarea',
                name : 'nrao_comment',
                fieldLabel: 'NRAO Comment',
            },{
                xtype: 'textarea',
                name : 'srp_to_pi',
                fieldLabel: 'SRP Comment to PI',
                readOnly: true,
                fieldCls: "x-pht-formfield-readonly"
            },{
                xtype: 'textarea',
                name : 'srp_to_tac',
                fieldLabel: 'SRP Comment to TAC',
                readOnly: true,
                fieldCls: "x-pht-formfield-readonly"
            },{
                xtype: 'textarea',
                name : 'tech_review_to_pi',
                fieldLabel: 'Tech Review to PI',
            },{
                xtype: 'textarea',
                name : 'tech_review_to_tac',
                fieldLabel: 'Tech Review to TAC',
                readOnly: true,
                fieldCls: "x-pht-formfield-readonly"
            },{
                xtype: 'textarea',
                name : 'tac_to_pi',
                fieldLabel: 'TAC Comments to PI',
            }],
            
        }];

        // must init for parent class
        this.buttons = [];

        this.callParent(arguments);
    },

    setProposalsStore: function(proposals){
        this.proposalsStore = proposals;
    },

    setProposalByPcode: function(pcode) {

        this.proposalCombo.setValue(pcode);
        this.setProposal(pcode, this.proposalsStore.findRecord('pcode', pcode));
    },

    setProposal: function(pcode, proposal) {
        this.proposalCombo.setValue(pcode);
        // load the proposal
        var form = this.down('form');
        form.loadRecord(proposal);
    },

    close: function() {
        this.hide();
    }
});            
