Ext.define('PHT.model.SourceCoordinateSystem', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'system'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/source/systems',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'source systems',
            successProperty: 'success'
        }
    }
});
