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
            'sessionlist toolbar button[action=delete]': {
                click: this.deleteSession
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
        });

        this.callParent(arguments);
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
        var session = grid.getSelectionModel().getLastSelected();
        this.confirmDelete(this.getSessionsStore(),
                      session,
                      'Deleting Session ' + session.get('name')
        );              
    },

    updateSession: function(button) {
        var win      = button.up('window'),
            form     = win.down('form'),
            session = form.getRecord(),
            values   = form.getValues();

        // don't do anything if this form is actually invalid
        var f = form.getForm();
        if (!(f.isValid())) {
            return;
        }

        session.set(values);
        // Is this a new session?
        if (session.get('id') == '') {
            session.save();
            var store = this.getSessionsStore();
             store.load({
                scope   : this,
                callback: function(records, operation, success) {
                    last = store.getById(store.max('id'));
                    form.loadRecord(last);
                }
            });
        } else {
            // set's the form to not dirty again.
            form.loadRecord(session);
            this.getSessionsStore().sync();
        }
    },
});
