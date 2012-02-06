Ext.define('PHT.model.Status', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'name'
             ],
    proxy: {
        type: 'ajax',
        url: 'proposal/statuses',
        reader: {
            type: 'json',
            root: 'statuses',
            successProperty: 'success'
        }
    }
});
