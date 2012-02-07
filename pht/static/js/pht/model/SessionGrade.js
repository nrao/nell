Ext.define('PHT.model.SessionGrade', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'grade'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/session/grades',
        reader: {
            type: 'json',
            root: 'session grades',
            successProperty: 'success'
        }
    }
});
