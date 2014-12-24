var events_timeseries_data = {
    labels: [],
    datasets: [
        {
            label: 'Events',
            data: [],
            fillColor: 'rgba(30, 30, 30, .2)',
            strokeColor: 'rgba(30, 30, 30, .8)',
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
        value: 100,
        label: 'Unresolved',
        color: 'red',
    },
    {
        value: 50,
        label: 'Resolved',
        color: 'green',
    },
    {
        value: 5,
        label: 'Acknowledged',
        color: 'yellow',
    }
];

document.addEventListener('DOMContentLoaded', function(){
    var ctx = document.getElementById('events_timeseries').getContext('2d');
    new Chart(ctx).Line(
        events_timeseries_data,
        {
            tooltipTemplate: "<%= value %>",
            responsive: true,
        }
    );

    ctx = document.getElementById('events_doughnut').getContext('2d');
    new Chart(ctx).Doughnut(events_doughnut_data);
});
