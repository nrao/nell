/*
We need to have the following comments accessible to the client: Technical reviews to TAC, (Same? TAC comments to PI, NRAO comments), SRP Science Review, Technical Review(s), SRP to TAC, TAC comments to NRAO (aka sched note).

The following should be editable in the GB PHT. TAC comments to PI, NRAO Comments, Technical Review(s), and TAC comments to NRAO.
*/

Ext.define('PHT.view.proposal.TacTool', {
    extend: 'Ext.window.Window',
    //extend: 'PHT.view.Edit',
    alias : 'widget.tactool',
    title : 'TAC Tool',
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
                    me.setProposal(pcode);
                }
            },
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,        
            ]},
        ];

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        // TBF: load the new proposal
        this.proposalCombo.setValue(pcode);
    },
});            
