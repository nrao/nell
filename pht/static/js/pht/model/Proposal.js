Ext.define('PHT.model.Proposal', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'pst_proposal_id'
           , 'proposal_type'
           , 'observing_types'
           , 'status'
           , 'semester'
           , 'pi_name'
           , 'pi_id'
           , 'authors'
           , 'sci_categories'
           , 'pcode'
           , 'create_date'
           , 'modify_date'
           , 'submit_date'
           , 'requested_time'
           , 'allocated_time'
           , 'title'
           , 'abstract'
           , 'spectral_line'
           , 'joint_proposal'
           , 'next_sem_complete'
           // from DSS project:
           , 'dss_pcode'
           , 'complete'
           , 'dss_total_time'
           , 'billed_time'
           , 'scheduled_time'
           , 'remaining_time'
           ], 
    proxy: {
        type: 'rest',
        url: '/pht/proposals',
        reader: {
            type: 'json',
            timeout: 300000,
            root: 'proposals',
            successProperty: 'success',
            totalProperty: 'total',
        }
    }
});
