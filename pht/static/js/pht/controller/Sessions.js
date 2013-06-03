Ext.define('PHT.controller.Sessions', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'Backend',
        'Receiver',
        'Session',
        'SessionName',
        'SessionGrade',
        'SessionType',
        'SessionObservingType',
        'SessionSeparation',
        'Semester',
        'WeatherType',
    ],

    stores: [
        'Backends',
        'Proposals',
        'Receivers',
        'Sessions',
        'SessionNames',
        'SessionGrades',
        'SessionTypes',
        'SessionObservingTypes',
        'SessionSeparations',
        'Semesters',
        'WeatherTypes',
    ],

    views: [
        'Edit',
        'Form',
        'proposal.Edit',
        'session.List',
        'session.Edit',
        'session.Form',
    ],

    init: function() {

        this.control({
            'sessionlist' : {
                itemdblclick: this.editSession
            },
            'sessionlist toolbar button[action=create]': {
                click: this.createSession
            },
            'sessionlist toolbar button[action=edit]': {
                click: this.editSelectedSessions
            },
            'sessionlist toolbar button[action=delete]': {
                click: this.deleteSession
            },
            'sessionlist toolbar button[action=duplicate]': {
                click: this.duplicateSession
            },
            'sessionlist toolbar button[action=clear]': {
                click: this.clearFilter
            },
            'sessionedit button[action=save]': {
                click: this.updateSession
            },             
            'sessionedit button[action=calculateLSTs]': {
                click: this.calculateLSTs
            },             
            'sessionedit button[action=generatePeriods]': {
                click: this.generatePeriods
            },             
        });

        this.selectedSessions = [];
        this.callParent(arguments);
        // helper class for keeping times correct
        this.accounting = Ext.create('PHT.controller.TimeAccounting');
    },

    setPeriodsWindow: function(periodsWindow) {
        this.periodsWindow = periodsWindow;
    },

    generatePeriods: function(button) {
        var win = button.up('window');
        var form = win.down('form');
        var session = form.getRecord();
        this.session = session
        var url = '/pht/sessions/' + session.get('id') + '/generatePeriods';

        // error check: make them save changes first
        var f = form.getForm()
        if (f.isDirty()) {
            Ext.Msg.alert('Warning', "Save changes before generating periods");    
            return
        }

        // the rest of the error checking is done server side
        Ext.Ajax.request({
           url: url,
           method: 'POST',
           scope: this,
           success: function(response) {
               var json = eval('(' + response.responseText + ')');
               var msg = json.message;
               // TBF: why can we only generate the success callback?
               if (json.success) {
                   // let them know how it went, then show new periods
                   Ext.Msg.show({
                        title: 'Info',
                        msg: msg,
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.INFO,
                        scope: this,
                        fn: function(id) {
                           // why can't I reused these variables from
                           // above?  why do I have only 'button'?
                           var win = button.up('window');
                           var form = win.down('form');
                           var session = form.getRecord();
                           var pcode      = session.get('pcode');
                               session_name = session.get('name');
                           var handle = session_name + " (" + pcode + ")";   
                           this.periodsWindow.down('periodlist').setHandle(handle);
                           this.periodsWindow.down('periodlist').getStore('Periods').load();
                           this.periodsWindow.show();                   
                        }
                    });
               } else {
                   // let them know what the problem was
                   Ext.Msg.alert('Warning', msg);
               }
           },
       });    
    },

    notify: function(data) {
        if (data['notification'] == 'proposalSelected') {
            this.sessionList.setProposal(data.pcode);
        }
    },

    calculateLSTs: function(button) {
        var win = button.up('window');
        var form = win.down('form');
        var session = form.getRecord();
        var url = '/pht/sessions/' + session.get('id') + '/calculateLSTs';

        // error check: make them save changes first
        var f = form.getForm()
        if (f.isDirty()) {
            Ext.Msg.alert('Warning', "Save changes before calculating LST's");    
            return
        }
        // need valid Ra / Dec
        var raField = f.findField('ra');
        var decField = f.findField('dec');
        if (!raField.isValid() | !decField.isValid()) {
            Ext.Msg.alert('Warning', "Cannot calculate LSTs with invalid Ra & Dec values.");
            return
        }
        if (session.get('ra') == "" | session.get('dec') == "") {
            Ext.Msg.alert('Warning', "Ra and Dec values necessary to calculate LSTs.");
            return
        }

        Ext.Ajax.request({
           url: url,
           method: 'POST',
           success: function(response) {
               var json = eval('(' + response.responseText + ')');

               // update our session and form with this result
               session.set('min_lst', json.data.minLstSexagesimel);
               session.set('max_lst', json.data.maxLstSexagesimel);
               session.set('center_lst', json.data.centerLstSexagesimel);
               session.set('lst_width', json.data.lstWidthSexagesimel);
               form.loadRecord(session)
           },
       });    
    },

    setSessionListWindow: function(sessionListWindow) {
        this.sessionListWindow = sessionListWindow;
    },

    setSessionList: function(sessionList) {
        this.sessionList = sessionList;
    },


    clearFilter: function(button) {
        var store = this.getStore('Sessions');
        if (store.isFiltered()){
            store.clearFilter()
        }
        var grid = button.up('sessionlist');
        grid.proposalCombo.reset();
        grid.rcvrCombo.reset();
        grid.sciCatCombo.reset();
    },

    createSession: function(button) {
        var session = Ext.create('PHT.model.Session', {});
        var view = Ext.widget('sessionedit');
        view.down('form').loadRecord(session);
    },

    editSelectedSessions: function(button) {
        var grid = button.up('grid');
        this.selectedSessions = grid.getSelectionModel().getSelection();

        if (this.selectedSessions.length <= 1) {
            this.editSession(grid, this.selectedSessions[0]);
        } else {
            var template = Ext.create('PHT.model.Session');
            var view = Ext.widget('sessionedit');
            var fields = view.down('form').getForm().getFields();
            fields.each(function(item, index, length) {
                var disabledItems = ['pcode',
                             'thermal_night',
                                 'rfi_night',
                             'optical_night',
                              'transit_flat',
                                'guaranteed',
                   'session_teim_calculated',
                                    ];
                if (disabledItems.indexOf(item.getName()) > -1) {
                    item.disable();
                }
                item.allowBlank = true;
            }, this);
            view.down('form').loadRecord(template);
        }
    },

    deleteSession: function(button) {
        var grid = button.up('grid');
        var sessions = grid.getSelectionModel().getSelection();
        this.confirmDeleteMultiple(this.getSessionsStore(),
                      sessions,
                      'Deleting Selected Sessions'
        );              
    },

    // when a session is deleted, we must make sure the proposal is 
    // updated appropriately.
    onDelete: function(records) {
        if (records.length == 0) {
            return;
        }
        
        // get the session's proposal
        var pcode = records[0].get('pcode');
        var store = this.getProposalsStore();
        var ind = store.find('pcode', pcode);
        var proposal = store.getAt(ind);

        // simple enough - we need to subtract out the times 
        for (var i=0; i < records.length; i++) {
            var session = records[i];
            this.accounting.updateProposalTimesFromSession(session, proposal, this.sub); 
            store.sync();
        }    

        // now deal with grades
        var newGrades = this.getProposalGrades(pcode, records);
        proposal.set('grades', newGrades.join(','));

    },

    duplicateSession: function(button) {
        var grid = button.up('grid');
        var session = grid.getSelectionModel().getLastSelected();
        var store = this.getSessionsStore();
        Ext.Msg.show({
            title: "Duplicating Session " + session.get('name'),
            msg: 'Are you sure?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            scope: this,
            fn: function(id) {
                if (id == 'yes') {
                    // copy the session
                    var newSession = this.copyRecord(store, session);
                    // make sure the proposal explorer updates properly
                    this.duplicateSessionForProposal(session);
                    // when the save is successfull on the server side,
                    // then we can copy over sources
                    newSession.save({
                        callback: function(s) {
                            store.load({
                               scope   : this,
                               callback: function(records, operation, success) {
                                  last = store.getById(store.max('id'));
                                  // now we can use these id's to 
                                  // copy over the session's sources
                                  var url = '/pht/sources/transfer';
                                  Ext.Ajax.request({
                                      url: url,
                                      params : { from : session.get('id'),
                                                 to   : last.get('id')},
                                      method: 'POST',
                                      scope: this,
                                      callback: function() {
                                          store.sync();
                                      },
                                  });    
                               }
                            });
                        },
                    });
                }
            }
        });
    },

    // so we can pass in the '+' operator like a function
    add: function(a, b) {
        return a + b;
    },

    
    // so we can pass in the '+' operator like a function (Haskell?)
    sub: function(a, b) {
        return a - b;
    },

    // make sure the proposal updates correctly when a session is duplicated
    duplicateSessionForProposal: function(session) {

        // get the session's proposal
        var pcode = session.get('pcode');
        var store = this.getProposalsStore();
        var ind = store.find('pcode', pcode);
        var proposal = store.getAt(ind);

        this.accounting.updateProposalTimesFromSession(session, proposal, this.add); 
        store.sync()

    },

    // update the given object with the value for the given fields
    getValues: function(record, values, fields) {
        for (var i=0; i < fields.length; i++ ) {
            var fieldName = fields[i];
            var value = record.get(fieldName);
            values[fieldName] = value;
        }
        return values;    
    },

    updateSession: function(button) {

        // first, store some of the original values so 
        // we can check for changes later
        var win      = button.up('window'),
            form     = win.down('form')
        var f = form.getForm();

        // here's the fields we care about
        sessFields = ['requested_time',
                      'repeats',
                      'allocated_time',
                      'allocated_repeats',
                      'outer_repeats',
                      'grade']
        if (this.selectedSessions.length <= 1) {
            record   = form.getRecord()
            var originalValues = {};
            originalValues = this.getValues(record, originalValues, sessFields);
        } else {
            var originalValues = {};
            for (i=0; i < this.selectedSessions.length; i++) {
                record = this.selectedSessions[i];
                var sId = record.get('id');
                var values = {}
                values = this.getValues(record, values, sessFields);
                originalValues[sId] = values;
            }
        }

        // here we actually change this session
        this.updateRecord(button
                        , this.selectedSessions
                        , this.getSessionsStore()
                         );

        // Now we must reset read-only fields, and update the Prop. Ex.
        // First, editing one, or multiple records?
        if (this.selectedSessions.length <= 1) {
            var record   = form.getRecord();
            var sTypeStore = this.getSessionTypesStore();
            var sType = sTypeStore.getAt(
                sTypeStore.find('type', record.get('session_type')));
            record.set('session_type_code', sType.get('abbreviation'));
            var f = form.getForm();
            if (f.isValid()) {
                this.updateReadOnlyFields(record);
                this.updateProposalExplorer(record, originalValues, sessFields);
                form.loadRecord(record);
            }        
        } else {
            var sTypeStore = this.getSessionTypesStore();
            for (i=0; i < this.selectedSessions.length; i++) {
                record = this.selectedSessions[i];
                var sType = sTypeStore.getAt(
                    sTypeStore.find('type', record.get('session_type')));
                record.set('session_type_code', sType.get('abbreviation'));
                this.updateReadOnlyFields(record);
            }
            this.updateProposalExplorerMulti(this.selectedSessions, originalValues, sessFields);
        }
        this.getSessionNamesStore().load();
        this.selectedSessions = [];                 
    },

    // some of the proposal fields are dependent on their sessions
    updateProposalExplorerMulti: function(sessions, originalValues, fieldNames) {
        // first, save some time by looking for if there are any changes
        var changes = false;
        for (var i=0; i < fieldNames.length; i++) {
            var fieldName = fieldNames[i];
            for (var j=0; j < sessions.length; j++) {
                var session = sessions[j];
                var sId = session.get('id');
                if (originalValues[sId][fieldName] != session.get(fieldName)) {
                    changes = true;
                }    
            }
        }
        if (changes == true) {
            // deal with the changes, one session at a time 
            for (var j=0; j < sessions.length; j++) {
                var session = sessions[j];
                var sId = session.get('id');
                this.updateProposalExplorer(session, originalValues[sId], fieldNames);
            }    
        }    
    },

    // some of the proposal fields are dependent on their sessions
    updateProposalExplorer: function(session, originalValues, fieldNames) {
        // first, just look if any of the fields we care about have changed
        var changes = false;
        for (var i=0; i < fieldNames.length; i++) {
            var fieldName = fieldNames[i];
            if (originalValues[fieldName] != session.get(fieldName)) {
                changes = true;
            }
        }
        if (changes == true) {
            // deal with the changes - get the session's proposal
            var pcode = session.get('pcode');
            var store = this.getProposalsStore();
            var ind = store.find('pcode', pcode);
            var proposal = store.getAt(ind);

            // requested time
            var time = parseFloat(originalValues['requested_time']);
            var reps = parseFloat(originalValues['repeats']);
            oldTime = this.accounting.calculateRequestedTime(time, reps);
            newTime = this.accounting.getTotalRequestedTime(session);                                                           
            this.accounting.updateProposalTime(oldTime, newTime, proposal, 'requested_time')
            // allocated time
            var time = parseFloat(originalValues['allocated_time']);
            var reps = parseFloat(originalValues['allocated_repeats']);
            var outs = parseFloat(originalValues['outer_repeats']);
            oldTime = this.accounting.calculateAllocatedTime(time
                                                           , reps
                                                           , outs);
            newTime = this.accounting.getTotalAllocatedTime(session);
            this.accounting.updateProposalTime(oldTime, newTime, proposal, 'allocated_time')

            // grades are also complicated
            var sOldGrade = originalValues['grade'];
            var sNewGrade = session.get('grade');
            if (sOldGrade != sNewGrade) {
                var none = [];
                var newGrades = this.getProposalGrades(pcode, none);
                proposal.set('grades', newGrades.join(','));
            }

            store.sync();
        }
    },

    getProposalGrades: function(pcode, avoidSessions) {
        // builid up a list of session ids to avoid
        var avoidIds = [];
        for (var i=0; i < avoidSessions.length; i++) {
            var session = avoidSessions[i];
            avoidIds.push(session.get('id'));
        }

        // what a pain in the ass - 
        // we need to look at all other sessions to figure
        // out how to change the proposal's grades
        sStore = this.getSessionsStore();
        newGrades = []
        // find each session w/ for this proposal
        ind = sStore.find('pcode', pcode);
        while (ind != -1) {
            var s = sStore.getAt(ind);
            // do we avoid using this session?
            if (avoidIds.indexOf(s.get('id')) == -1) { 
                var g = s.get('grade');
                // and see if we need to add it to the proposal's
                if (newGrades.indexOf(g) == -1) {
                    newGrades.push(g);
                }
            }    
            // is there another one?
            ind = sStore.find('pcode', pcode, ind+1);
        }     
        return newGrades
    },

    // some of the fields shown for the session are read only and
    // derived from other fields - we need to keep these up to date.
    updateReadOnlyFields: function(session) {
        var time = this.accounting.getTotalRequestedTime(session);
        session.set('requested_total', time);
        var time = this.accounting.getTotalAllocatedTime(session);
        session.set('allocated_total', time); 
        session.set('inner_repeats', session.get('allocated_repeats'));
        session.set('inner_separation', session.get('separation'));
        session.set('inner_interval', session.get('interval_time'));
    },

});
