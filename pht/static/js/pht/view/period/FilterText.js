Ext.define('PHT.view.period.FilterText', {
    extend: 'Ext.form.field.Text', 
    enableKeyEvents: true,
    listeners: {
        specialkey: function(textField, e, eOpts) {
            if (e.getKey() == e.ENTER) {
                var value = escapeRegEx(textField.getValue().toLowerCase());
                var store = textField.up('periodlist').getStore('Periods');
                store.filter([{
                    filterFn: function(item) {
                        console.log(value); 
                        console.log(item.get(textField.filterField).toLowerCase());
                        console.log(item.get(textField.filterField).toLowerCase().search(value));
                        return item.get(textField.filterField).toLowerCase().search(value) > -1;
                    }
                }]);
            }
        }
    },
});

// TBF: we need a utility area to put this stuff in 
function escapeRegEx(str) {
    // http://kevin.vanzonneveld.net
    // *     example 1: preg_quote("$40");
    // *     returns 1: '\$40'
    // *     example 2: preg_quote("*RRRING* Hello?");
    // *     returns 2: '\*RRRING\* Hello\?'
    // *     example 3: preg_quote("\\.+*?[^]$(){}=!<>|:");
    // *     returns 3: '\\\.\+\*\?\[\^\]\$\(\)\{\}\=\!\<\>\|\:'

    return (str+'').replace(/([\\\.\+\*\?\[\^\]\$\(\)\{\}\=\!\<\>\|\:])/g, "\\$1");

}
