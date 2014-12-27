var events_timeseries_data = {
    labels: [],
    datasets: [
        {
            label: 'Events',
            data: [],
            fillColor: 'rgba(34, 34, 34, .2)',
            strokeColor: 'rgba(34, 34, 34, .8)',
        }
    ],
};

var alerts_doughnut_data = [
    {
        value: Math.floor(Math.random() * 350) + 20,
        label: 'E-Mail',
        color: 'rgb(0,204,102)',
    },
    {
        value: Math.floor(Math.random() * 150) + 10,
        label: 'SMS',
        color: 'rgb(51,0,255)',
    },
    {
        value: Math.floor(Math.random() * 50) + 1,
        label: 'Voice',
        color: 'rgb(102,153,255)',
    }
];

document.addEventListener('DOMContentLoaded', function(){
    Chart.defaults.global.responsive = true;

    for(var bucket in timeseries){
        events_timeseries_data.datasets[0].data.push(timeseries[bucket]);
        var time = new Date(bucket * 1000.0);
        var label = (time.getHours() % 12)+ ':' + time.getMinutes() + ':00';
        events_timeseries_data.labels.push(label);
    }

    var ctx = document.getElementById('events_timeseries').getContext('2d');
    new Chart(ctx).Line(
        events_timeseries_data,
        {
            tooltipTemplate: "<%= value %>",
        }
    );

    var alert_count = document.getElementById('alert_count');
    var data = [
        {
            value: parseInt(alert_count.dataset.openCount),
            label: 'Open',
            color: 'rgb(250, 160, 160)',
        },
        {
            value: parseInt(alert_count.dataset.resolvedCount),
            label: 'Resolved',
            color: 'rgb(160, 250, 160)',
        },
        {
            value: parseInt(alert_count.dataset.ackCount),
            label: 'Acknowledged',
            color: 'rgb(255, 255, 150)',
        }
    ];
    new Chart(alert_count.getContext('2d')).Doughnut(data);

    ctx = document.getElementById('alerts_doughnut').getContext('2d');
    new Chart(ctx).Doughnut(alerts_doughnut_data);
});
