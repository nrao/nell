Ext.define('PHT.view.overview.Calendar', {
    extend: 'Ext.window.Window',
    width: '90%',
    height: '90%',
    layout: 'fit',
    constrain: true,
    maximizable: true,
    bodyStyle: {
        background: '#fff',
    }, 

    initComponent: function() {
        var me = this;
        var period = Ext.create('PHT.view.overview.Period');
        this.items = [
            Ext.create('Ext.draw.Component', {
                height: 400,
                width: 600,
                items: [{
                    type: 'path',
                    stroke: '#000',
                    path: me.generateGridPath(31),
                    },
                    period
                ]
            }),
        ];
        this.callParent(arguments);
    },

    generateGridPath: function(numDays) {
        var vspace  = 50;
        var hspace  = 25;
        var numCols = 25; // number of hours + 1
        var start   = 100;
        var width   = numCols * vspace + start - vspace;
        var numRows = numDays + 1;
        var height  = numRows * hspace + 10 - hspace;
        var path   = [];
        for (c = 0; c < numCols; c++) {
            path.push('M' + start + ' 10');
            path.push('L' + start + ' ' + height);
            start += vspace;
        }
        start  = 10;
        for (r = 0; r < numRows; r++) {
            path.push('M100 ' + start);
            path.push('L' + width + ' ' + start);
            start += hspace;
        }
        return path;
    },
});
