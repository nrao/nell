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
                itemdblclick: this.editSelectedSources
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
            console.log(f.getValues());
            f.submit({
                scope: this,
                url: 'sources/import',
                params: {
                    pcode: win.pcode, 
                },    
                waitMsg: 'Uploading your sources ...',
                success: function(fp, action) {
                    handleSourceUploadResult(action, win);
                    this.getProposalSourcesStore().load();
                },
            });
        }   
    },


    importSources: function(button) {
        var view = Ext.widget('sourceimport');
        // make sure this window knows who it is importing for
        var propSrcList = button.up('panel')
        console.log(propSrcList);
        var pcode = propSrcList.proposalCombo.getValue();
        console.log(pcode);
        view.setProposalCode(pcode);
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

    editSelectedSources: function(button) {
        var grid = button.up('grid');
        this.selectedSources = grid.getSelectionModel().getSelection();

        if (this.selectedSources.length <= 1) {
            this.editSource(grid, this.selectedSources[0]);
        } else {
            var template = Ext.create('PHT.model.ProposalSource');
            var view = Ext.widget('sourceedit');
            var fields = view.down('form').getForm().getFields();
            // what fields don't work with multi edit?
            fields.each(function(item, index, length) {
                var disabledItems = ['pcode', 'observed'];
                if (disabledItems.indexOf(item.getName()) > -1) {
                    item.disable();
                }
                item.allowBlank = true;
            }, this);
            view.down('form').loadRecord(template);
        }
    },

    updateSource: function(button) {
        this.updateRecord(button
                        , this.selectedSources
                        , this.getProposalSourcesStore()
                         );
        this.selectedSources = []      
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

// Utilities

// Major TBF: we don't seem to be returning the right
// thing from the server: we ALWAYS get our success
// callback, and when we do, we can't use o.result,
// which *should* be the decoded JSON response.
// So, instead, we have to parse the raw response.
function handleSourceUploadResult(action, win) {
    var failureStr = '</span>success<span class="q">"</span></span>: <span class="bool">false</span>';
    var response = action.response.responseText;
    var startFailureStr = response.search(failureStr);
    if (startFailureStr != -1) {
        var startErrMsg = response.search("errorMsg");
        var msg = "There was an error uploading your sources (none have been saved)";
        if (startErrMsg < startFailureStr) {
            var len = startFailureStr - startErrMsg;
            var msgDetails = response.substr(startErrMsg, len);
             msg += ': \n' + msgDetails;
        } else {
            msg += '.';
        }                
        Ext.Msg.alert('Failure', msg);
    } else {
        Ext.Msg.alert('Info', 'Your sources have been uploaded.');
        win.close()
    }
}

