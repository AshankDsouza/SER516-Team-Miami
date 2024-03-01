document.addEventListener("DOMContentLoaded", function() {
    // Sample data for demonstration
    const days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"];
    const storyPointsData = [5, 4, 6, 3, 7];
    const bvPointsData = [3, 2, 5, 1, 6];

    // Chart.js configuration
    const ctx = document.getElementById('partial-work-done-chart').getContext('2d');
    const consistencyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [{
                label: 'Story Points',
                data: storyPointsData,
                borderColor: 'rgba(255, 99, 132, 1)', // Red color for story points
                borderWidth: 2,
                fill: false
            }, {
                label: 'B.V. Points',
                data: bvPointsData,
                borderColor: 'rgba(54, 162, 235, 1)', // Blue color for B.V. points
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Points'
                    }
                }
            }
        }
    });
});
