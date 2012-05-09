Ext.define('PHT.view.source.SessionList' ,{
    extend: 'Ext.grid.Panel',
    alias : 'widget.sessionsourcelist',
    store : 'SessionSources', 

    multiSelect: true,

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
        
        this.sessionCombo = Ext.create('Ext.form.field.ComboBox', {
            name: 'session',
            store: 'Sessions',
            queryMode: 'local',
            lastQuery: '',
            displayField: 'name',
            valueField: 'id',
            hideLabel: true,
            emptyText: 'Select a session...',
            listeners: {
                select: function(combo, record, index) {
                    var session_id = record[0].get('id');
                    grid.setSession(session_id);
                }
            },
        });

        this.viewConfig = {
            plugins: {
                ptype: 'gridviewdragdrop',
                dragGroup: 'sessionSourceGridDDGroup',
                dropGroup: 'proposalSourceGridDDGroup',
            },
            listeners: {
                beforedrop: function(node, data, dropRec, dropPosition, dropFunction) {
                    if (grid.sessionCombo.getValue() == null) {
                        return false;
                    }

                    var pcode = grid.proposalCombo.getValue();
                    for (i = 0; i < data.records.length; i++) {
                        rec = grid.getStore('SessionSources').getById(data.records[i].get('id'));
                        if (rec != null) {
                            return false;
                        }
                        if (data.records[i].get('pcode') != pcode) {
                            return false;
                        }
                    }
                }, 

                drop: function(node, data, dropRec, dropPosition) {
                    var dropOn = dropRec ? ' ' + dropPosition + ' ' + dropRec.get('name') : ' on empty view';
                    var session = grid.sessionCombo.getValue();
                    for (i = 0; i < data.records.length; i++) {
                        record = data.records[i];
                        url = '/pht/sessions/' + session + '/sources/' + record.get('id');
                        Ext.Ajax.request({
                           url: url,
                           method: 'POST',
                        });

                        grid.getSelectionModel().deselectAll();
                    }
                }
            }
        };

        this.dockedItems = [{
            xtype: 'toolbar',
            items: [
                this.proposalCombo,
                this.sessionCombo,
                { xtype: 'tbseparator'},
                Ext.create('Ext.button.Button', {
                    text: 'Remove Sources',
                    action: 'remove',
                }),
                Ext.create('Ext.button.Button', {
                    text: 'Average RA/Dec',
                    action: 'average',
                }),
            ]
        }];

        this.columns = this.buildColumns();

        //this.columns = this.buildColumns();
        // TBF: Trying to get multiple grid instances to work. :(
        /*
        config = Ext.apply({}, {columns: this.buildColumns()});
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        */

        this.callParent(arguments);
    },

    setProposal: function(pcode) {
        var store = this.sessionCombo.getStore();
        if (store.isFiltered()){
            store.clearFilter();
        }
        store.filter("pcode", pcode);
        //this.sessionCombo.clearValue();

        // Also setting the proposal combo's value to the pcode in case
        // this method was called from outside the grid, i.e. from the 
        // proposal editor.
        this.proposalCombo.setValue(pcode);
    },

    setSession: function(session_id) {
        var store = this.getStore('SessionSources');
        // Setting a new proxy with the url for the selected session
        store.setProxy(
        {
            type: 'rest',
            url: '/pht/sessions/' + session_id + '/sources',
            reader: {
                type : 'json',
                root: 'sources',
                successProperty: 'success'
            }
        });
        store.load();
        this.sessionCombo.setValue(session_id);
    },

    buildColumns: function() {
        return [
            {header: 'Proposal',          dataIndex: 'pcode',             width: 100},
            {header: 'Target Name',       dataIndex: 'target_name',       width: 100},
            {header: 'Coord. Sys.',       dataIndex: 'coordinate_system', flex: 1},
            {header: 'RA',                dataIndex: 'ra',                flex: 1},
            {header: 'Dec',               dataIndex: 'dec',               flex: 1},
            {header: 'RA Range',          dataIndex: 'ra_range',          flex: 1},
            {header: 'Dec Range',         dataIndex: 'dec_range',         flex: 1},
            {header: 'Velocity Units',    dataIndex: 'velocity_units',    flex: 1},
            {header: 'Velocity Redshift', dataIndex: 'velocity_redshift', flex: 1},
            {header: 'Convention',        dataIndex: 'convention',        flex: 1},
            {header: 'Ref. Frame',        dataIndex: 'reference_frame',   flex: 1},
            {header: 'Allowed',           dataIndex: 'allowed',        flex: 1},
            {header: 'Observed',          dataIndex: 'observed',   flex: 1},
        ];

    },
});
