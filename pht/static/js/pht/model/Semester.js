Ext.define('PHT.model.Semester', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'semester'
             ],
    proxy: {
        type: 'ajax',
        url: 'semesters',
        reader: {
            type: 'json',
            root: 'semesters',
            successProperty: 'success'
        }
    }
});
