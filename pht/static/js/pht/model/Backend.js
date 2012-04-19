Ext.define('PHT.model.Backend', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'name',
             'abbreviation',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/backends',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'backends',
            successProperty: 'success'
        }
    }
});
