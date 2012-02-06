Ext.define('PHT.model.WeatherType', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'type'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/weather/types',
        reader: {
            type: 'json',
            root: 'weather types',
            successProperty: 'success'
        }
    }
});
