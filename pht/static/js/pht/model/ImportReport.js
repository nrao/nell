Ext.define('PHT.model.ImportReport', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'create_date',
             'report',
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/import_reports',
        reader: {
            type: 'json',
            root: 'import_reports',
            successProperty: 'success'
        }
    }
});
