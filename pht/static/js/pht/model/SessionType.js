Ext.define('PHT.model.SessionType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type',
             'abbreviation',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/session/types',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'session types',
            successProperty: 'success'
        }
    }
});
