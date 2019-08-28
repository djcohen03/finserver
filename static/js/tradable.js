$(function() {

    var makeOptions = (prices, times, title, lastprice) => {
        return {
            chart: {
                height: 350,
                type: 'line'
            },
            stroke: {
                curve: 'straight',
                width: 2,
                dashArray: [0, 5],
                colors: ['#2E93fA', '#999999']
            },
            series: [{
                name: "Prices",
                data: prices
            }, {
              name: 'Previous Close',
              data: times.map(() => lastprice)
            }],
            grid: {
                row: {
                    colors: ['#f3f3f3', 'transparent'],
                    opacity: 0.5
                },
            },
            xaxis: {
                categories: times,
                tickAmount: 20,
                type: 'time',
                title: {
                    text: 'Day Session Time'
                }
            },
            title: {
                text: title,
                align: 'center'
            }
        }
    }

    var chart = null;
    var chartElement = $("#chart")[0];
    $('.fetch-chart').on('click', function() {
        var url = $(this).attr('data-href');
        $.ajax({
            url: url,
            success: response => {
                var data = JSON.parse(response);
                var title = `${data.tradable}: ${data.date}`;
                var options = makeOptions(data.prices, data.times, title, data.lastprice);

                if (chart === null) {
                    chart = new ApexCharts(chartElement, options);
                    chart.render();
                } else {
                    chart.updateOptions(options);
                }
            },
            error: () => {
                console.error('...');
            }
        });




    });
});
