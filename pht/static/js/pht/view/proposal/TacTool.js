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
