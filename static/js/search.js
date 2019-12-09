
var SEACH = (function() {
    // Define the global SEARCH module:

    // Bind search method:
    var bindSearch = options => {
        // First Get a handle on the UI elements, based on the provided 'searcher'
        // and 'items' option arguments:
        var searcher = $(options.searcher)
        var items = $(options.items);

        // Bind search functionality:
        searcher.on('input', function() {
            var value = $(this).val().toUpperCase();
            if (value !== '') {
                items.each(function() {
                    var item = $(this);
                    var text = item.text();
                    item.toggle(text.indexOf(value) >= 0);
                });
            } else {
                // Show all:
                items.show();
            }
        });
    }

    var methods = {};
    methods.bind = bindSearch
    return methods

})()
