Ext.define('PHT.model.WeatherType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: 'weather/types',
        reader: {
            type: 'json',
            root: 'weather types',
            successProperty: 'success'
        }
    }
});
