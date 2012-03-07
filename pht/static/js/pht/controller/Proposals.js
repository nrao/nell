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
        'PstProposalCode',
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
        'PstProposalCodes',
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
                itemdblclick: this.editProposal,
                itemclick: this.filterSessionExplorer,
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

    filterSessionExplorer: function(grid, record) {
        this.notifyObservers({notification: 'filterSessionExplorer'
                            , pcode : record.get('pcode')});
    },

    // How to respond to click's on the navigation tree?
    editTreeNode: function(view, record, item, index, event) {
        // The id is of form type=value, but we could also use
        // record.raw.store and record.raw.semester/pcode/sessionId
        // to figure this all out.
        var parts = record.internalId.split('=');
        var type = parts[0];
        var value = parts[1];
        if (type != 'semester') {
            if (record.raw.store == 'Proposals') {
                var item = this.getStore(record.raw.store).getById(value);
                this.editProposal(view, item);
            } else if (record.raw.store == 'Sessions') {
                var id = parseInt(value);
                var item = this.getStore(record.raw.store).getById(id);
                this.editSession(view, item);
            }
        }
    },

    importProposalForm: function(button) {
        var view      = Ext.widget('proposalimport');
        var grid      = button.up('grid');
        var proposals = grid.getSelectionModel().getSelection();
        var fields    = view.down('form').getForm().getFields();
        var pcodeCB   = fields.filter('name', 'pcode').first();
        var selected  = [];
        for (i=0; i < proposals.length; i++) {
            selected.push([proposals[i].get('pcode')]);
        }
        pcodeCB.setValue(selected);
    },

    importProposalFormByProposal: function() {
        var view = Ext.widget('proposalimport');
        var form = view.down('form');
        var f = form.getForm()
        f.setValues({proposalsCheckbox : 'on'});
    },

    importProposalFormBySemester: function() {
        var view = Ext.widget('proposalimport');
        var form = view.down('form');
        var f = form.getForm()
        f.setValues({semesterCheckbox : 'on'});
    },    

    importProposalFormByPstProposal: function() {
        var view = Ext.widget('proposalimport');
        var form = view.down('form');
        var f = form.getForm()
        f.setValues({pstProposalsCheckbox : 'on'});
    },

    refresh: function() {
        console.log('refreshing');
        this.getProposalsStore().load();
        // TBF, BUG: this causes the tree to hang
        //this.getProposalTreeStore().load();
        this.getProposalCodesStore().load();
        this.getSessionsStore().load();
        this.notifyObservers({notification: 'newImport'});
        console.log('done');
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
                    me.refresh();
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
                    me.refresh();
                },
                
             });
        } else if (values.pstProposalsCheckbox == 'on') {
            Ext.Ajax.request({
                url: '/pht/import/pst',
                params: {
                    proposals: values.pcode
                },
                method: 'POST',
                timeout: 300000,
                success: function(response) {
                    win.close();
                    me.refresh();
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
        this.updateRecord(button
                        , this.selectedProposals
                        , this.getProposalsStore()
                         );
        this.selectedProposals = [];                  
    },
});
