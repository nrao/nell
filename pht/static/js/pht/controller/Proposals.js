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
        'Sessions',
        'ProposalTree',
    ],

    views: [
        'Edit',
        'Form',
        'proposal.List',
        'proposal.ListWindow',
        'proposal.Edit',
        'proposal.Import',
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
            'proposallist toolbar button[action=edit]': {
                click: this.editSelectedProposals
            },
            'proposallist toolbar button[action=delete]': {
                click: this.deleteProposal
            },
            'proposallist toolbar button[action=clear]': {
                click: this.clearFilter
            },
            'proposallist toolbar button[action=import]': {
                click: this.importProposalForm
            },
            'proposaledit button[action=save]': {
                click: this.updateProposal
            },            
            'proposalimport button[action=import]': {
                click: this.importProposal
            },            
            'proposalnavigate': {
                itemclick: this.editTreeNode
            }, 
            
        });        

        this.selectedProposals = [];
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

    importProposalForm: function(button) {
        var view      = Ext.widget('proposalimport');
        var grid      = button.up('grid');
        var proposals = grid.getSelectionModel().getSelection();
        var fields    = view.down('form').getForm().getFields();
        var pcodeCB   = fields.filter('name', 'pcode').last();
        var selected  = [];
        for (i=0; i < proposals.length; i++) {
            selected.push([proposals[i].get('pcode')]);
        }
        pcodeCB.setValue(selected);
    },

    importProposal: function(button) {
        var me     = this;
        var win    = button.up('window');
            form   = win.down('form');
            values = form.getValues();

        win.setLoading(true);
        if (values.proposalsCheckbox == 'on'){
            Ext.Ajax.request({
                url: '/pht/import',
                params: {
                    proposals: values.pcode
                },
                method: 'POST',
                timeout: 300000,
                success: function(response) {
                    win.close();
                    me.getProposalsStore().load();
                    me.getProposalTreeStore().load();
                    me.getProposalCodesStore().load();
                    me.getSessionsStore().load();
                },
             });
        } else if (values.semesterCheckbox == 'on') {
            Ext.Ajax.request({
                url: '/pht/import/semester',
                params: {
                    semester: values.semester
                },
                method: 'POST',
                timeout: 300000,
                success: function(response) {
                    win.close();
                    me.getProposalsStore().load();
                    me.getProposalTreeStore().load();
                    me.getProposalCodesStore().load();
                    me.getSessionsStore().load();
                },
             });
        } else {
            win.close();
        }
    },

    createProposal: function(button) {
        var proposal = Ext.create('PHT.model.Proposal');
        var view = Ext.widget('proposaledit');
        view.down('form').loadRecord(proposal);
    },

    deleteProposal: function(button) {
        var grid = button.up('grid');
        var proposals = grid.getSelectionModel().getSelection();
        var store  = this.getProposalsStore();
        Ext.Msg.show({
             title: 'Deleting Selected Proposals',
             msg: 'Are you sure?',
             buttons: Ext.Msg.YESNO,
             icon: Ext.Msg.QUESTION,
             scope: this,
             fn: function(id) {
                 if (id == 'yes') {
                     for (i = 0; i < proposals.length; i++) {
                         proposals[i].destroy();
                     }
                     store.remove(proposals);
                 }
             }
        });
    },
    
    editProposal: function(grid, record) {
        var view   = Ext.widget('proposaledit');
        view.filterPis(record.get('pcode'));
        view.down('form').loadRecord(record);        
    },   

    editSelectedProposals: function(button) {
        var grid = button.up('grid');
        this.selectedProposals = grid.getSelectionModel().getSelection();

        if (this.selectedProposals.length <= 1) {
            this.editProposal(grid, this.selectedProposals[0]);
        } else {
            var template = Ext.create('PHT.model.Proposal');
            var view = Ext.widget('proposaledit');
            var fields = view.down('form').getForm().getFields();
            fields.each(function(item, index, length) {
                var disabledItems = ['pcode', 'pi_id', 'joint_proposal'];
                if (disabledItems.indexOf(item.getName()) > -1) {
                    item.disable();
                }
                item.allowBlank = true;
            }, this);
            view.down('form').loadRecord(template);
        }
    },

    updateProposal: function(button) {
        var win      = button.up('window'),
            form     = win.down('form'),
            proposal = form.getRecord(),
            values   = form.getValues();

        if (this.selectedProposals.length <= 1) {
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
        } else {
            var dirty_items = form.getForm().getFieldValues(true);
            real_items = {}
            for (var i in dirty_items) {
                if (values[i] != '') {
                    real_items[i] = values[i];
                }
            }
            for (i=0; i < this.selectedProposals.length; i++) {
                this.selectedProposals[i].set(real_items);
            }
            this.getProposalsStore().sync();
            this.selectedProposals = [];
            win.close();
        }
    },
});
