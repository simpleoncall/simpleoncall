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

for(var i = -3600; i <= 0;i+=300){
    var value = Math.floor(Math.random() * 100);
    events_timeseries_data.datasets[0].data.push(value);
    var now = new Date((parseInt(new Date().getTime() / 1000.0) + i) * 1000.0);
    var label = ((now.getHours() + 1) % 12)+ ':' + now.getMinutes() + ':00';
    events_timeseries_data.labels.push(label);
}

var events_doughnut_data = [
    {
        value: Math.floor(Math.random() * 150),
        label: 'Unresolved',
        color: 'rgb(250, 160, 160)',
    },
    {
        value: Math.floor(Math.random() * 150),
        label: 'Resolved',
        color: 'rgb(160, 250, 160)',
    },
    {
        value: Math.floor(Math.random() * 150),
        label: 'Acknowledged',
        color: 'rgb(255, 255, 150)',
    }
];

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

    var ctx = document.getElementById('events_timeseries').getContext('2d');
    new Chart(ctx).Line(
        events_timeseries_data,
        {
            tooltipTemplate: "<%= value %>",
        }
    );

    ctx = document.getElementById('events_doughnut').getContext('2d');
    new Chart(ctx).Doughnut(events_doughnut_data);

    ctx = document.getElementById('alerts_doughnut').getContext('2d');
    new Chart(ctx).Doughnut(alerts_doughnut_data);
});
