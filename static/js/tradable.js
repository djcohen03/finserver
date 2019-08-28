$(function() {

    var makeOptions = (prices, times, title) => {
        return {
            chart: {
                height: 350,
                type: 'line'
            },
            stroke: {
                curve: 'straight'
            },
            series: [{
                name: "Prices",
                data: prices
            }],
            grid: {
                row: {
                    colors: ['#f3f3f3', 'transparent'],
                    opacity: 0.5
                },
            },
            xaxis: {
                categories: times,
                tickAmount: 20
            },
            title: {
                text: title,
                style: {
                    fontSize: '12px',
                    fontFamily: 'Helvetica, Arial, sans-serif',
                    cssClass: 'apexcharts-xaxis-title',
                },
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
                var options = makeOptions(data.prices, data.times, title);

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
