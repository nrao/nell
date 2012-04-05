Ext.define('PHT.controller.Sessions', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'Backend',
        'Receiver',
        'Session',
        'SessionGrade',
        'SessionType',
        'SessionObservingType',
        'SessionSeparation',
        'Semester',
        'WeatherType',
    ],

    stores: [
        'Backends',
        'Receivers',
        'Sessions',
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
            'proposaledit button[action=sessions]': {
                click: this.proposalSessions
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
            this.sessionListWindow.down('sessionlist').setProposal(data.pcode);
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

    proposalSessions: function(button) {
        var win = button.up('window');
            form = win.down('form');
            proposal = form.getRecord();
        var pcode = proposal.get('pcode');
        this.sessionListWindow.down('sessionlist').setProposal(pcode);
        this.sessionListWindow.show();
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

    deleteSession: function(button) {
        var grid = button.up('grid');
        var sessions = grid.getSelectionModel().getSelection();
        this.confirmDeleteMultiple(this.getSessionsStore(),
                      sessions,
                      'Deleting Selected Sessions'
        );              
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
                    this.copyRecord(store, session);
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
                          });    
                       }
                    });
                }
            }
        });
        
    },

    updateSession: function(button) {
        this.updateRecord(button
                        , this.selectedSessions
                        , this.getSessionsStore()
                         );
        this.selectedSessions = [];                 
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
});
