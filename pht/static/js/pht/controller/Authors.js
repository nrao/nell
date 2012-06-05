Ext.define('PHT.controller.Authors', {
    extend: 'PHT.controller.PhtController',
   
    models: [
        'Author',
        'Proposal',
        'PstUser',
    ],

    stores: [
        'Authors',
        'Proposals',
        'PstUsers',
    ],

    views: [
        'proposal.Edit',
        'author.List',
        'author.ListWindow',
        'author.Edit',
    ],

    init: function() {

        this.control({
            'authorlist' : {
                itemdblclick: this.editAuthor
            }, 
            'authorlist toolbar button[action=create]': {
                click: this.createAuthor
            },
            'authorlist toolbar button[action=delete]': {
                click: this.deleteAuthor
            },
            'authoredit button[action=save]': {
                click: this.updateAuthor
            },            
            'proposaledit button[action=authors]' : {
                click: this.proposalAuthors
            },
        });

        this.callParent(arguments);
    },

    setProposalAuthorsWindow: function(proposalAuthorsWindow) {
        this.proposalAuthorsWindow = proposalAuthorsWindow;
    },

    proposalAuthors: function(button) {
        var form = button.up('form'),
            proposal = form.getRecord();
        var pcode = proposal.get('pcode');
        this.proposalAuthorsWindow.down('authorlist').setProposal(pcode);
        this.proposalAuthorsWindow.show();
    },

    createAuthor: function(button) {
        var pcode  = button.up('toolbar').down('combo').getValue();
        var author = Ext.create('PHT.model.Author', {pcode : pcode});
        var view   = Ext.widget('authoredit');
        view.down('form').loadRecord(author);
    },

    deleteAuthor: function(button) {
        var grid = button.up('grid');
        var authors = grid.getSelectionModel().getSelection();
        this.confirmDeleteMultiple(this.getAuthorsStore(),
                      authors,
                      'Deleting Selected Authors'
        );              
    },

    editAuthor: function(grid, record) {
        var view   = Ext.widget('authoredit');
        view.down('form').loadRecord(record);        
    },   

    updateAuthor: function(button) {
        var win      = button.up('window'),
            form     = win.down('form'),
            author   = form.getRecord(),
            values   = form.getValues();

        // don't do anything if this form is actually invalid
        var f = form.getForm();
        if (!(f.isValid())) {
            return;
        }

        author.set(values);
        // Is this a new proposal?
        if (author.get('id') == '') {
            author.save();
            this.getAuthorsStore().insert(0, [author]);
        } else {
            this.getAuthorsStore().sync();
        }
        win.close();
    },
   
});
