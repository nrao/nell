Ext.define('PHT.model.SessionSeparation', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'separation'
             ],
    proxy: {
        type: 'ajax',
        url: 'session/separations',
        reader: {
            type: 'json',
            root: 'session separations',
            successProperty: 'success'
        }
    }
});
