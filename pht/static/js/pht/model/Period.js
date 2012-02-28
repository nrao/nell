Ext.define('PHT.model.Period', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'session'
           , 'session_id'
           , 'pcode'
           , 'handle'
           , 'date'
           , 'time'
           , 'duration'
           ], 
    proxy: {
        type: 'rest',
        url: '/pht/periods',
        reader: {
            type: 'json',
            root: 'periods',
            successProperty: 'success'
        }
    }
});
