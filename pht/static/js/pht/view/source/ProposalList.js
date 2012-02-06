Ext.define('PHT.view.source.ProposalList' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.proposalsourcelist',
    store : 'ProposalSources', 

    multiSelect: true,
    viewConfig: {
        copy: true,
        plugins: {
            ptype: 'gridviewdragdrop',
            dragGroup: 'proposalSourceGridDDGroup',
            dropGroup: 'sessionSourceGridDDGroup',
        },
    },

    initComponent: function() {
        var grid = this; // capturing "this" to have the proper scope below
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
                    grid.setProposal(pcode);
                }
            },
        });

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,
                { xtype: 'tbseparator' },
                Ext.create('Ext.button.Button', {
                    text: 'Create Sources',
                    action: 'create',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Delete Sources',
                    action: 'delete',
                }),
            ]
        }];

        this.columns = [
            {header: 'Proposal', dataIndex: 'pcode', width: 100},
            {header: 'Target Name', dataIndex: 'target_name', width: 100},
            {header: 'Coord. Sys.', dataIndex: 'coordinate_system', flex: 1},
            {header: 'RA', dataIndex: 'ra',  flex: 1},
            {header: 'Dec', dataIndex: 'dec',  flex: 1},
            {header: 'RA Range', dataIndex: 'ra_range',  flex: 1},
            {header: 'Dec Range', dataIndex: 'dec_range',  flex: 1},
            {header: 'Velocity Units', dataIndex: 'velocity_units',  flex: 1},
            {header: 'Velocity Redshift', dataIndex: 'velocity_redshift',  flex: 1},
            {header: 'Convention', dataIndex: 'convention',  flex: 1},
            {header: 'Ref. Frame', dataIndex: 'reference_frame',  flex: 1},
            {header: 'Allowed', dataIndex: 'allowed',  flex: 1},
            {header: 'Observed', dataIndex: 'observed',  flex: 1},
        ];

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        var store = this.getStore('ProposalSources');
        // Setting a new proxy with the url for the selected proposal
        store.setProxy(
        {
            type: 'rest',
            url: '/pht/proposals/' + pcode + '/sources',
            reader: {
                type : 'json',
                root: 'sources',
                successProperty: 'success'
            }
        });
        store.load();
        // Also setting the proposal combo's value to the pcode in case
        // this method was called from outside the grid, i.e. from the 
        // proposal editor.
        this.proposalCombo.setValue(pcode);
    },
});
