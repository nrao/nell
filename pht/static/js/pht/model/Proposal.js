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
           , 'total_time'
           , 'title'
           , 'abstract'
           , 'joint_proposal'
           ], 
    proxy: {
        type: 'rest',
        url: '/pht/proposals',
        reader: {
            type: 'json',
            root: 'proposals',
            successProperty: 'success'
        }
    }
});
