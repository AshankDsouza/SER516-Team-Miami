document.addEventListener('DOMContentLoaded', function() {
    // Data for the chart
    var data = {
        labels: ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5'], // Sample labels for tasks
        datasets: [{
            label: 'Task Cycle Time',
            data: [8, 12, 10, 14, 18], // Sample data for Task Cycle Time
            backgroundColor: 'rgba(54, 162, 235, 0.2)', // Blue color for Task Cycle Time
            borderColor: 'rgba(54, 162, 235, 1)', // Border color for Task Cycle Time
            borderWidth: 1
        }]
    };

    // Configuration options for the chart
    var options = {
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Days' 
                }
            }
        }
    };

    // Get the canvas element
    var ctx = document.getElementById('myChart').getContext('2d');

    // Create the bar chart
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
});
