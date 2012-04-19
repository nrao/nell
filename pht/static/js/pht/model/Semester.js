Ext.define('PHT.model.Semester', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'semester'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/semesters',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'semesters',
            successProperty: 'success'
        }
    }
});
