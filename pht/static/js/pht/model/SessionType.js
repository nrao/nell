Ext.define('PHT.model.SessionType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/session/types',
        reader: {
            type: 'json',
            root: 'session types',
            successProperty: 'success'
        }
    }
});
