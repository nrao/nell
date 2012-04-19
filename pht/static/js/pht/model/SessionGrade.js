Ext.define('PHT.model.SessionGrade', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'grade'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/session/grades',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'session grades',
            successProperty: 'success'
        }
    }
});
