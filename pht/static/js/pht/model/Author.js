Ext.define('PHT.model.Author', {
    extend: 'Ext.data.Model',
    fields: ['id'
           , 'pst_person_id'
           , 'pst_author_id'
           , 'pcode'
           , 'affiliation'
           , 'domestic'
           , 'new_user'
           , 'email'
           , 'address'
           , 'telephone'
           , 'last_name'
           , 'first_name'
           , 'name'
           , 'professional_status'
           , 'thesis_observing'
           , 'graduation_year'
           , 'oldauthor_id'
           , 'storage_order'
           , 'other_awards'
           , 'support_requester'
           , 'supported'
           , 'budget'
           , 'assignment'
           ],
    proxy: {
        type: 'rest',
        url: '/pht/authors',
        reader: {
            type: 'json',
            root: 'authors',
            successProperty: 'success'
        }
    }
});
