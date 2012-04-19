Ext.define('PHT.model.SourceConvention', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'convention'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/source/conventions',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'source conventions',
            successProperty: 'success'
        }
    }
});
