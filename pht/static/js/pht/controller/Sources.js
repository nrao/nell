Ext.define('PHT.controller.Sources', {
    extend: 'PHT.controller.PhtController',

    models: [
        'ProposalSource',
        'SessionSource',
        'SourceCoordinateEpoch',
        'SourceCoordinateSystem',
        'SourceVelocityType',
        'SourceConvention',
        'SourceReferenceFrame',
    ],

    stores: [
        'ProposalSources',
        'SessionSources',
        'Sessions',
        'SourceCoordinateEpochs',
        'SourceCoordinateSystems',
        'SourceVelocityTypes',
        'SourceConventions',
        'SourceReferenceFrames',
    ],

    views: [
        'Edit',
        'Form',
        'proposal.Edit',
        'session.Edit',
        'source.ProposalList',
        'source.ProposalListWindow',
        'source.SessionList',
        'source.SessionListWindow',
        'source.Edit',
        'source.Import',
    ],

    init: function() {

        this.control({
            'proposaledit button[action=sources]': {
                click: this.proposalSources
            },
            'sessionedit button[action=sources]': {
                click: this.sessionSources
            },
            // proposal source grid:
            'proposalsourcelist' : {
                itemdblclick: this.editSource
            },
            'proposalsourcelist toolbar button[action=create]': {
                click: this.createSource
            },
            'proposalsourcelist toolbar button[action=delete]': {
                click: this.deleteSource
            },
            'sessionsourcelist toolbar button[action=remove]': {
                click: this.removeSourceFromSession
            },
            'sessionsourcelist toolbar button[action=average]': {
                click: this.averageRADec
            },
            // TBF?: session source grid:
            // source form:
            'sourceedit button[action=save]': {
                click: this.updateSource
            },             
            'proposalsourcelist toolbar button[action=import]': {
                click: this.importSources
            },
            'sourceimport button[action=import]': {
                click: this.uploadFile
            },             
        });

        this.sessionForms = {};

        this.callParent(arguments);
    },

    notify: function(data) {
        this.sessionForms[data.session.id] = data;
    },

    uploadFile: function(button) {
        var win = button.up('window');
        var form = win.down('form');
        var f = form.getForm()
        if(f.isValid()){
            f.submit({
                url: 'sources/import',
                waitMsg: 'Uploading your sources man...',
                success: function(fp, o) {
                    // Major TBF: we don't seem to be returning the right
                    // thing from the server: we ALWAYS get our success
                    // callback, and when we do, we can't use o.result,
                    // which *should* be the decoded JSON response.
                    // So, instead, we have to parse the raw response.
                    var failureStr = '</span>success<span class="q">"</span></span>: <span class="bool">false</span>'
                    var response = o.response.responseText
                    if (response.search(failureStr) != -1) {
                        Ext.Msg.alert('Failure', 'There was an error uploading the file.');
                    } else {
                        Ext.Msg.alert('Info', 'Your sources have been uploaded.');
                    }
                },
            });
        }   
    },

    importSources: function(button) {
        var view = Ext.widget('sourceimport');
    },

    setProposalSourcesWindow: function(proposalSourcesWindow) {
        this.proposalSourcesWindow = proposalSourcesWindow;
    },

    setSessionSourcesWindow: function(sessionSourcesWindow) {
        this.sessionSourcesWindow = sessionSourcesWindow;
    },

    proposalSources: function(button) {
        var win = button.up('window');
            form = win.down('form');
            proposal = form.getRecord();
        var pcode = proposal.get('pcode');
        this.proposalSourcesWindow.down('proposalsourcelist').setProposal(pcode);
        this.proposalSourcesWindow.show();
    },

    sessionSources: function(button) {
        var win     = button.up('window');
            form    = win.down('form');
            session = form.getRecord();
        var pcode      = session.get('pcode');
            session_id = session.get('id');

        this.sessionSourcesWindow.down('sessionsourcelist').setProposal(pcode);
        this.sessionSourcesWindow.down('sessionsourcelist').setSession(session_id);
        this.sessionSourcesWindow.show();
    },

    createSource: function(button) { 
        // For which proposal are we creating this source?
        var grid = button.up('grid');
        var pcode = grid.proposalCombo.getValue();
        // NOTE: using model.ProposalSource since we are calling this from
        // Proposal Source grid.
        // Also, make sure the new source has some default values set.
        var source = Ext.create('PHT.model.ProposalSource'
            , { pcode: pcode,
                allowed: 'unknown'
        });
        var view = Ext.widget('sourceedit');
        view.down('form').loadRecord(source);
    },

    deleteSource: function(button) {
        var grid = button.up('grid');
        var source = grid.getSelectionModel().getLastSelected();
        this.confirmDelete(this.getProposalSourcesStore(),
                           source,
                           'Deleting Source ' + source.get('target_name'));
    },
    
    editSource: function(grid, record) {
        var view = Ext.widget('sourceedit');
        view.down('form').loadRecord(record);        
    },

    updateSource: function(button) {
        var win      = button.up('window'),
            form     = win.down('form'),
            source = form.getRecord(),
            values   = form.getValues();

        // don't do anything if this form is actually invalid
        var f = form.getForm();
        if (!(f.isValid())) {
            return;
        }

        source.set(values);
        // Is this a new source?
        // NOTE: using model.ProposalSource since we are only updating from Prop. Src. grid
        if (source.get('id') == '') {
            source.save();
            var store = this.getProposalSourcesStore();
            store.load({
                scope   : this,
                callback: function(records, operation, success) {
                    var last = store.getById(store.max('id'));
                    form.loadRecord(last);
                }
            });
            //this.getProposalSourcesStore().insert(0, [source]);
        } else {
            this.getProposalSourcesStore().sync();
        }    
    },

    removeSourceFromSession: function(button) {
        var grid = button.up('grid');
        var sources = grid.getSelectionModel().getSelection();
        var session = grid.sessionCombo.getValue();
        for (i = 0; i < sources.length; i++) {
            source =  sources[i].get('id');
            url = '/pht/sessions/' + session + '/sources/' + source;
            Ext.Ajax.request({
               url: url,
               method: 'DELETE',
            });
        }
        grid.getStore('SessionSources').load();
    },

    averageRADec: function(button) {
        var grid = button.up('grid');
        var controller = this;
        var sources = grid.getSelectionModel().getSelection();
        if (sources.length == 0) {
            return null;
        }
        var store   = this.getSessionsStore();
        var session = store.getById(grid.sessionCombo.getValue());
        var url     = '/pht/sessions/' + session.get('id') + '/averageradec';
        var source_ids = new Array();
        for (i = 0; i < sources.length; i++) {
            source_ids.push(sources[i].get('id'));
        }
        Ext.Ajax.request({
           url: url,
           params: {
               sources: source_ids
           },
           method: 'POST',
           success: function(response) {
               console.log('average response: ');
               console.log(response);
               var json = eval('(' + response.responseText + ')');
               console.log(json);


               // update our session record with this result
               session.set('ra', json.data.ra_sexagesimel);
               session.set('dec', json.data.dec_sexagesimel);

               // Update the form
               var data = controller.sessionForms[session.id];
               if (data != null && !data.form.isDestroyed) {
                   data.form.loadRecord(session);
               }

           },
        });
    },


});
