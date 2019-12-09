$(function() {
    // Bind search functionality:
    SEACH.bind({
        searcher: '.search-tradables',
        items: '.tradables-list > .list-group-item'
    });


    var onChange = () => {
        var symbols = getSelected();

        // Update the Banner:
        var banner = $('#selected-symbols');
        var copy = symbols.length ? symbols.join(', ') : 'Choose some assets to the left...';
        banner.text(copy);

        // Update the buttons:
        $('.actions .btn').toggleClass('disabled', symbols.length < 2);

    }




    // Bind click functionality:
    $('.tradables-list > a').click(function() {
        $(this).toggleClass('active');

        onChange();
    });

    $('#clear-selected').click(() => {
        $('.tradables-list > .list-group-item').removeClass('active');
        $('#table-container').html('');
        onChange();
    })


    var tableUI = {
        th: item => `<th>${item}</th>`,
        td: item => `<td>${item}</td>`,
        trh: items => `<tr>${items.map(tableUI.th).join('')}</tr>`,
        tr: items => `<tr>${items.map(tableUI.td).join('')}</tr>`,
    }

    var makeTable = (symbols, matrix) => {
        // Make the header:
        var thead = tableUI.trh([''].concat(symbols));
        var tbody = matrix.map((row, index) => {
            var symbol = `<b>${symbols[index]}</b>`;
            return tableUI.tr([symbol].concat(row));
        }).join('');

        return `
            <div class="panel panel-default">
                <div class="panel-heading">Correlation Matrix</div>
                <table class='table'>
                    <thead>${thead}</thead>
                    <tbody>${tbody}</tbody>
                </table>
            </div>
        `
    }



    $('#correlation-submit').click(function () {
        var symbols = getSelected();

        // Make sure not too many are selected:
        if (symbols.length > 40) {
            FLASH.error('Please Limit to 40 Items');
            return
        }



        // Disable this button:
        $(this).addClass('disabled');

        var args = {
            'symbols': symbols
        }
        var container = $('#table-container');
        var loading = '<p class="text-center">Loading...</p>'
        container.html(loading);

        $.ajax({
            url: '/api/v1/correlation?' + $.param(args),
            success: response => {
                var data = JSON.parse(response);
                var matrix = data.correlations;
                var table = makeTable(data.symbols, matrix);
                container.html(table);

            },
            error: response => {
                container.html('');
                FLASH.error('An Error Occurred, Please Try Again Later');
            }
        });
    });



    // Get a list of the selected symbols:
    var getSelected = () => {
        var items = $('.tradables-list > .list-group-item');
        var active = items.filter((i, item) => $(item).hasClass('active'));
        var symbols = active.map((i, item) => $(item).text()).toArray();
        return symbols.sort();
    }

});
