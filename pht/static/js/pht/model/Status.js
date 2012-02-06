Ext.define('PHT.model.Status', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'name'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/proposal/statuses',
        reader: {
            type: 'json',
            root: 'statuses',
            successProperty: 'success'
        }
    }
});
