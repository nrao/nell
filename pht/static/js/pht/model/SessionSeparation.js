Ext.define('PHT.model.SessionSeparation', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'separation'
             ],
    proxy: {
        type: 'ajax',
        url: 'session/separations',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'session separations',
            successProperty: 'success'
        }
    }
});
