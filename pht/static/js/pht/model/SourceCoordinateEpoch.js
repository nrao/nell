Ext.define('PHT.model.SourceCoordinateEpoch', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'epoch'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/source/epochs',
        reader: {
            type: 'json',
            root: 'source epochs',
            successProperty: 'success'
        }
    }
});
