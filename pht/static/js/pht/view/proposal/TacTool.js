/*
We need to have the following comments accessible to the client: Technical reviews to TAC, (Same? TAC comments to PI, NRAO comments), SRP Science Review, Technical Review(s), SRP to TAC, TAC comments to NRAO (aka sched note).

The following should be editable in the GB PHT. TAC comments to PI, NRAO Comments, Technical Review(s), and TAC comments to NRAO.
*/

Ext.define('PHT.view.proposal.TacTool', {
    extend: 'PHT.view.Form',
    alias : 'widget.tactool',
    title : 'TAC Tool',
    autoScroll: true,
    border: false,
    trackResetOnLoad: true,
    fieldDefaults: {
       labelStyle: 'font-weight:bold',
    },
    defaults: {
        width: 450,
        height: 100,
        allowBlank: true,
        labelStyle: '',    
        layout: 'fit',
    },

    listeners: {
        // enable the save button when a change is made
        dirtychange: function(form, dirty) {
            if (dirty) {
                this.saveBtn.enable(true);
            } else {
                this.saveBtn.disable(true);
            }
       }
    },

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

        this.items = [
            {
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
        }];
        console.log(this.items);

        this.allocateBtn = Ext.create('Ext.button.Button', {
            text: 'Allocate',
            action: 'allocate',
        });
   
        this.saveBtn = Ext.create('Ext.Button', {
            text: 'Save',
            action: 'save',
            disabled: true,
        });

        this.buttons = [
            this.saveBtn,
        ];

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,        
                { xtype: 'tbseparator'},
                this.allocateBtn,
            ]},
        ];

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
        this.loadRecord(proposal);
    },
});            
