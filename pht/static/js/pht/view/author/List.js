Ext.define('PHT.view.author.List' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.authorlist',
    store : 'Authors', 

    initComponent: function() {
        var grid = this; // capturing "this" to have the proper scope below
        this.proposalCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'pcode',
            store: 'Proposals',
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
                    text: 'Create Author',
                    action: 'create',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Delete Author(s)',
                    action: 'delete',
                }),
            ]
        }];

        this.columns = [
            {header: 'Proposal', dataIndex: 'pcode', width: 100},
            {header: 'Name', dataIndex: 'name', width: 100},
            {header: 'Affiliation', dataIndex: 'affiliation', width: 100},
            {header: 'Email', dataIndex: 'email', width: 100},
            {header: 'Telephone', dataIndex: 'telephone', width: 100},
            {header: 'Address', dataIndex: 'address', width: 100},
            {header: 'Domestic', dataIndex: 'domestic', flex: 1},
            {header: 'New User', dataIndex: 'new_user', flex: 1},
            {header: 'Prof. Status', dataIndex: 'professional_status', width: 100},
            {header: 'Thesis Obs.', dataIndex: 'thesis_observing', flex: 1},
            {header: 'Grad. Year', dataIndex: 'graduation_year', flex: 1},
            {header: 'Old Author ID', dataIndex: 'oldauthor_id', flex: 1},
            {header: 'Storage Order', dataIndex: 'storage_order', flex: 1},
            {header: 'Other Awards', dataIndex: 'other_awards', flex: 1},
            {header: 'Support Requester', dataIndex: 'support_requester', flex: 1},
            {header: 'Supported', dataIndex: 'supported', flex: 1},
            {header: 'Budget', dataIndex: 'budget', flex: 1},
            {header: 'Assignment', dataIndex: 'assignment', width: 200},
        ];

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        var store = this.getStore();
        // Setting a new proxy with the url for the selected proposal
        store.setProxy(
        {
            type: 'rest',
            url: '/pht/proposals/' + pcode + '/authors',
            reader: {
                type : 'json',
                root: 'authors',
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
