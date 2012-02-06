// TBFs:
//  * how to keep the navigation tree up to date with changes elsewhere 
//    that affect it?  ex change which proposals a session has.

Ext.define('PHT.controller.Proposals', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'ObservingType',
        'PrimaryInvestigator',
        'Proposal',
        'ProposalType',
        'ProposalCode',
        'Status',
        'ScienceCategory',
        'Semester',
    ],

    stores: [
        'ObservingTypes',
        'PrimaryInvestigators',
        'Proposals',
        'ProposalCodes',
        'ProposalTypes',
        'ScienceCategories',
        'Statuses',
        'Semesters',
        'ProposalTree',
    ],

    views: [
        'proposal.List',
        'proposal.ListWindow',
        'proposal.Edit',
        'proposal.Navigate',
    ],

    init: function() {

        this.control({
            'proposallist' : {
                itemdblclick: this.editProposal
            },
            'proposallist toolbar button[action=create]': {
                click: this.createProposal
            },
            'proposallist toolbar button[action=delete]': {
                click: this.deleteProposal
            },
            'proposallist toolbar button[action=clear]': {
                click: this.clearFilter
            },
            'proposaledit button[action=save]': {
                click: this.updateProposal
            },            
            'proposalnavigate': {
                itemclick: this.editTreeNode
            }, 
            
        });        

        this.callParent(arguments);
    },

    clearFilter: function(button) {
        var store = this.getStore('Proposals');
        if (store.isFiltered()){
            store.clearFilter()
        }
        var grid = button.up('proposallist');
        grid.authorsFilterText.reset();
        grid.pcodeFilterText.reset();
        grid.titleFilterText.reset();
    },

    editTreeNode: function(view, record, item, index, event) {
        var item = this.getStore(record.raw.store).getById(record.internalId);
        if (record.raw.store == 'Proposals') {
            this.editProposal(view, item);
        } else if (record.raw.store == 'Sessions') {
            this.editSession(view, item);
        }
    },

    // Proposals:
    createProposal: function(button) {
        var proposal = Ext.create('PHT.model.Proposal');
        var view = Ext.widget('proposaledit');
        view.down('form').loadRecord(proposal);
    },

    deleteProposal: function(button) {
        var grid = button.up('grid');
        var proposal = grid.getSelectionModel().getLastSelected();
        this.confirmDelete(this.getProposalsStore(),
                           proposal,
                           'Deleting Proposal ' + proposal.get('pcode'));
    },
    
    editProposal: function(grid, record) {
        var view   = Ext.widget('proposaledit');
        view.filterPis(record.get('pcode'));
        view.down('form').loadRecord(record);        
    },   

    updateProposal: function(button) {
        var win      = button.up('window'),
            form     = win.down('form'),
            proposal = form.getRecord(),
            values   = form.getValues();

        // don't do anything if this form is actually invalid
        var f = form.getForm();
        if (!(f.isValid())) {
            return;
        }

        proposal.set(values);
        // Is this a new proposal?
        if (proposal.get('id') == '') {
            proposal.save();
            var store = this.getProposalsStore();
            store.load({
                scope   : this,
                callback: function(records, operation, success) {
                    var last = store.getById(store.max('id'));
                    form.loadRecord(last);
                }
            });    
        } else {
            this.getProposalsStore().sync();
        }
    },
});
