Ext.define('PHT.model.SessionName', {
    extend: 'Ext.data.Model',
    fields: [ 'id',
              'session',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/options?mode=session_names',
        reader: {
            type: 'json',
            root: 'session names',
            successProperty: 'success'
        }
    }
});
