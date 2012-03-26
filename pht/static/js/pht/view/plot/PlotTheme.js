Ext.define('PHT.view.plot.PlotTheme', {
    extend: 'Ext.chart.theme.Base',

    getColors: function(color) {
        var c = new Ext.draw.Color.fromString(color);
        var c1 = c.getLighter(0.15);
        var c2 = c.getLighter(0.30);
        return [c, c1, c2];
    } ,

    constructor: function(config) {
        this.callParent([Ext.apply({
            axisTitleLeft: {
              font: 'bold 8px Arial'
            },            
            axisTitleBottom: {
              font: 'bold 8px Arial'
            },            
        }, config)]);
    },
    
});

Ext.define('Ext.chart.theme.LstPressureThemeTotal', {
    extend: 'PHT.view.plot.PlotTheme',
 
    constructor: function(config) {

        var blues = this.getColors('#0000FF');
        var greens = this.getColors('#00FF00');
        var reds = this.getColors('#FF0000');

        var colors = ['orange',
              reds[0].toString(),
              reds[1].toString(), 
              reds[2].toString(), 
              greens[0].toString(),
              greens[1].toString(), 
              greens[2].toString(), 
              blues[0].toString(),
              blues[1].toString(), 
              blues[2].toString(), 
             ];        

        this.callParent([Ext.apply({
            colors: colors,
        }, config)]);
    }
});


Ext.define('Ext.chart.theme.LstPressureThemePoor', {
    extend: 'PHT.view.plot.PlotTheme',
 
    constructor: function(config) {

        var reds = this.getColors('#FF0000');
        
        var colors = ['orange',
              reds[0].toString(),
              reds[1].toString(), 
              reds[2].toString(), 
        ];

        this.callParent([Ext.apply({
            colors: colors
        }, config)]);
    }
});


Ext.define('Ext.chart.theme.LstPressureThemeGood', {
    extend: 'PHT.view.plot.PlotTheme',
 
    constructor: function(config) {

        var greens = this.getColors('#00FF00');
        
        var colors = ['orange',
              greens[0].toString(),
              greens[1].toString(), 
              greens[2].toString(), 
        ];

        this.callParent([Ext.apply({
            colors: colors
        }, config)]);
    }
});

Ext.define('Ext.chart.theme.LstPressureThemeEx', {
    extend: 'PHT.view.plot.PlotTheme',
 
    constructor: function(config) {

        var blues = this.getColors('#0000FF');
        
        var colors = ['orange',
              blues[0].toString(),
              blues[1].toString(), 
              blues[2].toString(), 
        ];

        this.callParent([Ext.apply({
            colors: colors
        }, config)]);
    }
});
