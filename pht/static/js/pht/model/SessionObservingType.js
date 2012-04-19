Ext.define('PHT.model.SessionObservingType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/session/observing/types',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'observing types',
            successProperty: 'success'
        }
    }
});
