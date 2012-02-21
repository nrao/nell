Ext.define('PHT.view.period.FilterText', {
    extend: 'Ext.form.field.Text', 
    enableKeyEvents: true,
    listeners: {
        specialkey: function(textField, e, eOpts) {
            if (e.getKey() == e.ENTER) {
                var value = textField.getValue().toLowerCase();
                var store = textField.up('periodlist').getStore('Periods');
                store.filter([{
                    filterFn: function(item) {
                        return item.get(textField.filterField).toLowerCase().search(value) > -1;
                    }
                }]);
            }
        }
    },
});
