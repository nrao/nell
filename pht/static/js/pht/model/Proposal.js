Ext.define('PHT.model.Proposal', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'pst_proposal_id'
           , 'proposal_type'
           , 'observing_types'
           , 'obs_type_codes'
           , 'status'
           , 'semester'
           , 'friend_name'
           , 'friend_id'
           , 'pi_name'
           , 'pi_id'
           , 'authors'
           , 'sci_categories'
           , 'sci_cat_codes'
           , 'pcode'
           , 'create_date'
           , 'modify_date'
           , 'submit_date'
           , 'requested_time'
           , 'allocated_time'
           , 'grades'
           , 'title'
           , 'abstract'
           , 'spectral_line'
           , 'joint_proposal'
           , 'next_sem_complete'
           , 'normalizedSRPScore'
           // from DSS project:
           , 'dss_pcode'
           , 'complete'
           , 'dss_total_time'
           , 'billed_time'
           , 'scheduled_time'
           , 'remaining_time'
           // comments
           , 'nrao_comment'
           , 'srp_to_pi'
           , 'srp_to_tac'
           , 'tech_review_to_pi'
           , 'tech_review_to_tac'
           , 'tac_to_pi'
           , 'tac_to_tac'
           ], 
    proxy: {
        type: 'rest',
        url: '/pht/proposals',
        timeout: 300000,
        reader: {
            type: 'json',
            root: 'proposals',
            successProperty: 'success',
            totalProperty: 'total',
        }
    }
});
