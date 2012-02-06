Ext.define('PHT.model.SessionSource', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'pcode'
           , 'name'
           , 'target_name'
           , 'coordinate_system'
           , 'ra'
           , 'dec'
           , 'ra_range'
           , 'dec_range'
           , 'velocity_units'
           , 'velocity_redshift'
           , 'convention'
           , 'reference_frame'
           , 'allowed'
           , 'observed'
           // raw PST values (readonly)
           , 'pst_ra'
           , 'pst_dec'
           , 'pst_ra_range'
           , 'pst_dec_range'
           ], 
});
