Ext.define('PHT.model.Period', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'session'
           , 'session_json'
           , 'session_id'
           , 'pcode'
           , 'handle'
           , 'date'
           , 'time'
           , 'duration'
           , 'window_size'
           , 'session_type_code'
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