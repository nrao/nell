Ext.define('PHT.store.ProposalTree', {
    extend: 'Ext.data.TreeStore',
    autoLoad: true,
    /*
    The proxy is for the url: http://trent.gb.nrao.edu:####/tree
    that serves up JSON like:
    {
    "proposals": [
        {
            "text": "GBT12A-337",
            "pcode": "GBT12A-337",
            "leaf": false,
            "id": "GBT12A-337"
        },
    ],    
    "success": "ok"    
    }
    */
    proxy: {
        type : 'ajax',
        url : 'tree',
        reader: {
            type: 'json',
            root: 'proposals',
            successProperty: 'success'
        },
    },
    root: {
        text : 'Proposals',
        expanded: true,
    }
});
