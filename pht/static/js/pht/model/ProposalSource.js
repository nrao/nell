Ext.define('PHT.model.ProposalSource', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'pcode'
           , 'target_name'
           , 'coordinate_system'
           , 'coordinate_epoch'
           , 'ra'
           , 'dec'
           , 'ra_range'
           , 'dec_range'
           , 'velocity_units'
           , 'velocity_redshift'
           , 'convention'
           , 'reference_frame'
           , 'observed'
           , 'allowed'
           // raw PST values (readonly)
           , 'pst_ra'
           , 'pst_dec'
           , 'pst_ra_range'
           , 'pst_dec_range'
           ], 
    proxy: {
        type: 'rest',
        url: '/pht/sources',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'sources',
            successProperty: 'success'
        }
    }
           
});
