Ext.application({
    name: 'HelloExt',
    launch: function() {
    Ext.create('Ext.panel.Panel', {
        renderTo: Ext.getBody(),
        width:  '100%',
        height: '100%',
        title: 'Green Bank Telescope - Proposal Handling Tool',
        layout: 'border',
        defaults: {
            collapsible: true,
            split: true,
            bodyStyle: 'padding:15px'
        },
        items: [
            {
                title: 'Dash Board',
                region: 'south',
                height: 250,
                minSize: 75,
                maxSize: 250,
                cmargins: '5 0 0 0'
            },{
                title: 'Navigation',
                region:'west',
                margins: '5 0 0 0',
                cmargins: '5 5 0 0',
                width: 175,
                minSize: 100,
                maxSize: 250
            },{
                title: 'Main Content',
                collapsible: false,
                region:'center',
                margins: '5 0 0 0'
            }]
        });
    }
});
