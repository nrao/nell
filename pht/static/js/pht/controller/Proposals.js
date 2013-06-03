// TBFs:
//  * how to keep the navigation tree up to date with changes elsewhere 
//    that affect it?  ex change which proposals a session has.

Ext.define('PHT.controller.Proposals', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'Friend',
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
        'Friends',
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
        'proposal.Export',
        'proposal.Navigate',
        'proposal.TacTool',
        'proposal.Allocate',
        'proposal.ProposalSummaryForm',
        'proposal.ProposalWorksheetForm',
    ],

    init: function() {

        this.control({
            'proposallist' : {
                itemdblclick: this.editProposal,
                itemclick: function(grid, record) {
                    this.proposalSelected(grid, record);
                    this.editProposal(grid, record);
                },
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
            'tactool button[action=save]': {
                click: this.updateProposal
            },            
            'tactool toolbar button[action=allocate]': {
                click: this.allocateForm
            },
            'proposalallocate button[action=save]': {
                click: this.allocateProposal
            },            
            'proposalallocate button[action=clear]': {
                click: this.allocateClearProposal
            },            
            'proposalimport button[action=import]': {
                click: this.importProposal
            },            
            'proposalexport button[action=export]': {
                click: this.exportProposal
            },            
            'proposalsummaryform button[action=submit]': {
                click: this.proposalSummary
            },            
            'proposalworksheetform button[action=submit]': {
                click: this.proposalWorksheet
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
        grid.testingFilter.toggle(true);
    },

    // load the form for allocating grades and time to proposal
    allocateForm: function(button) {
        var view     = button.up('viewport').down('tactool');
        var allocate = Ext.create('PHT.view.proposal.Allocate');
        var pcode    = view.proposalCombo.getValue();
        
        allocate.setProposal(pcode);
        allocate.setTitle('Allocate for Proposal ' + pcode);
        allocate.show();
    },

    // assing grades & allocated time to proposal
    allocateProposal: function(button) {
        var win = button.up('window')
        var form = win.down('form')
        // what was entered in the form?
        var values = form.getValues();
        var grade = values['grade']
        var scale = values['scale']
        var time  = values['time']
        // we want only sessions for this proposal
        var pcode = win.pcode;
        var store = this.getStore('Sessions');
        store.filter('pcode', pcode);
        // Now set each session's attributes accordingly
        // We do this on the client side instead of the server side
        // because it makes refreshing the sessions easier.
        var cnt = store.getCount();
        var pAllocated = 0.0;
        
        for (i=0; i < cnt; i++) {
            var session = store.getAt(i);
            // change session's grade
            if ((grade != null) && (grade != '')) {
                session.set('grade', grade);
            }
            // change session's allocated time.
            if ((time != null) && (time != '')) {
                // is the time value an absolute value,
                // or a scaling factor?
                if (scale == 'true') {
                    var requested = parseFloat(session.get('requested_time'));
                    var repeats = parseFloat(session.get('repeats'));
                    //var allocated = requested * repeats * (parseFloat(time)/100.0);
                    var allocatedRepeats = repeats
                    var allocated = requested * (parseFloat(time)/100.0);
                } else {
                    var repeats = parseFloat(session.get('repeats'));
                    var allocated = parseFloat(time) / repeats;
                    var allocatedRepeats = repeats;
                }
                pAllocated += allocated * allocatedRepeats
                session.set('allocated_time', allocated);
                session.set('allocated_repeats', allocatedRepeats);
                session.set('allocated_total', allocated * allocatedRepeats);
            }
            session.save()
        }
        store.sync();

        // update the proposal
        var pStore = this.getStore('Proposals');
        var proposal = pStore.findRecord('pcode', pcode);
        if ((time != null) && (time != '')) {
            proposal.set('allocated_time', pAllocated);
        }
        if ((grade != null) && (grade != '')) {
            proposal.set('grades', grade);
        }
        
        pStore.sync();
        
        win.hide();
    },

    // clear all sessions' grades to None and times to zero
    allocateClearProposal: function(button) {
        var win = button.up('window')
        var pcode = win.pcode;
        // sessions
        var store = this.getStore('Sessions');
        store.filter('pcode', pcode);
        var cnt = store.getCount();
        for (i=0; i < cnt; i++) {
            var session = store.getAt(i);
            session.set('allocated_time', 0.0);
            session.set('grade', null);
        }    
        store.sync()
        // update the proposal
        var pStore = this.getStore('Proposals');
        var proposal = pStore.findRecord('pcode', pcode);
        proposal.set('allocated_time', 0.0);
        proposal.set('grades', '');
        pStore.sync();
        win.hide();
    },

    proposalSelected: function(grid, record) {
        var pcode = record.get('pcode');
        this.notifyObservers({notification: 'proposalSelected'
                            , pcode : pcode});
        // part of this controller, so we don't need notification
        this.tacTool.setProposal(pcode, record);
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

    exportProposalsForm: function() {
        var view = Ext.widget('proposalexport');
        var form = view.down('form');
        var f = form.getForm()
    },

    proposalSummaryForm: function() {
        var view = Ext.widget('proposalsummaryform');
    },

    proposalWorksheetForm: function() {
        var view = Ext.widget('proposalworksheetform');
    },

    refresh: function() {
        this.getProposalsStore().load();
        this.getProposalTreeStore().load();
        this.getProposalCodesStore().load();
        this.getSessionsStore().load();
        this.notifyObservers({notification: 'newImport'});
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
                    semester: values.semester,
                    srp:      values.srp,
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
    
    exportProposal: function(button) {
        var me     = this;
        var win    = button.up('window');
            form   = win.down('form');
            values = form.getValues();

        win.setLoading(true);
        if (values.proposalsCheckbox == 'on'){
            Ext.Ajax.request({
                url: '/pht/export',
                params: {
                    proposals: values.pcode,
                    astrid:   values.astrid
                },
                method: 'POST',
                timeout: 300000,
                success: function(response) {
                    win.close();
                },
             });
        } else if (values.semesterCheckbox == 'on') {
            Ext.Ajax.request({
                url: '/pht/export/semester',
                params: {
                    semester: values.semester,
                    astrid:   values.astrid
                },
                method: 'POST',
                timeout: 300000,
                success: function(response) {
                    win.close();
                },
                
             });
        } else {
            win.close();
        }
    },

    proposalSummary: function(button) {
        var url = '/pht/reports/proposalsummary';
        this.semesterSomethingSubmit(button, url);
    },

    proposalWorksheet: function(button) {
        var url = '/pht/reports/proposalworksheet';
        this.semesterSomethingSubmit(button, url);
    },
    
    semesterSomethingSubmit: function(button, baseurl) {
        var win    = button.up('window'),
            form   = win.down('form'),
            values = form.getValues();
        var url = baseurl + '?semester=' + values.semester
                  + '&allocated=' + values.allocated;
        window.open(url);
        win.close();
    },

    createProposal: function(button) {
        var proposal = Ext.create('PHT.model.Proposal');
        var view = button.up('viewport').down('proposaledit');
        view.loadRecord(proposal);
    },

    deleteProposal: function(button) {
        var grid = button.up('grid');
        var proposals = grid.getSelectionModel().getSelection();
        this.confirmDeleteMultiple(this.getProposalsStore(),
                                   proposals,
                                   'Deleting Selected Proposals'
        );
    },
    
    editProposal: function(grid, record) {
        var view = grid.up('viewport').down('proposaledit');
        view.filterPis(record.get('pcode'));
        view.setRecord(record);
        view.loadRecord(record);        
    },   

    editSelectedProposals: function(button) {
        var grid = button.up('grid');
        this.selectedProposals = grid.getSelectionModel().getSelection();

        if (this.selectedProposals.length <= 1) {
            this.editProposal(grid, this.selectedProposals[0]);
        } else {
            var template = Ext.create('PHT.model.Proposal');
            var view = button.up('viewport').down('proposaledit');
            view.prepMultiEditFields();
            view.loadRecord(template);
        }
    },

    // overrid this simple function so that we can add the pi's name
    // which is needed to see the explorer update.
    setRecord: function(record, values) {
            // first, get the Primary Investigator record
            // that corresponds to the id we've got
            var store = this.getPrimaryInvestigatorsStore()
            var pi_id = values['pi_id'];
            var ind = store.find('id', pi_id);
            if (ind > 0) {
                var pi = store.getAt(ind);
                // now extract their name and add it to our values
                var pi_name = pi.get('name');
                values['pi_name'] = pi_name;
            }
            record.set(values);
    },

    updateProposal: function(button) {
        this.updateRecord(button
                        , this.selectedProposals
                        , this.getProposalsStore()
                         );
        this.selectedProposals = [];                  
        var view = button.up('viewport').down('proposaledit');
        view.resetMultiEditFields();
    },

    setTacTool: function(tacTool) {
        this.tacTool = tacTool;
        this.tacTool.setProposalsStore(this.getProposalsStore());
    },
});
