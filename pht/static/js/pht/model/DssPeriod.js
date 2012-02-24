Ext.define('PHT.model.DssPeriod', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'session'
           , 'session_id' // Not provided
           , 'pcode'      // Not provided
           , 'handle'
           , 'date'
           , 'time'
           , 'duration'
           ], 
    proxy: {
        type: 'ajax',
        url: '/scheduler/periods/UTC',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'periods',
            successProperty: 'success'
        }
    }
});
