$(function() {

    // Configure the search feature:
    $('.search-tradables').on('input', function() {
        var value = $(this).val().toUpperCase();
        if (value !== '') {
            $('.tradables-list > .list-group-item').each(function() {
                var item = $(this);
                var text = item.text();
                item.toggle(text.indexOf(value) >= 0);
            });
        } else {
            $('.tradables-list > .list-group-item').show();
        }
    });

})
