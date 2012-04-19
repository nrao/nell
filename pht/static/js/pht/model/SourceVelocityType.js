Ext.define('PHT.model.SourceVelocityType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/source/velocity_types',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'source velocity types',
            successProperty: 'success'
        }
    }
});
