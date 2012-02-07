Ext.define('PHT.model.SourceReferenceFrame', {
    extend: 'Ext.data.Model',
    fields: ['id',
             'frame'
             ],
    proxy: {
        type: 'ajax',
        url: '/pht/source/reference_frames',
        reader: {
            type: 'json',
            root: 'source reference frames',
            successProperty: 'success'
        }
    }
});
