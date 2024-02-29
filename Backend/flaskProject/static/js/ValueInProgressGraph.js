document.addEventListener("DOMContentLoaded", function() {
    // Sample data for demonstration
    const days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"];
    const storyPointsData = [5, 4, 6, 3, 7];

    // Calculate ratio of story points for each day
    const ratioData = storyPointsData.map((points, index) => points / (index + 1));

    // Chart.js configuration
    const ctx = document.getElementById('partial-work-done-chart').getContext('2d');
    const valueInProgressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: days,
            datasets: [{
                label: 'Story Points Ratio',
                data: ratioData,
                backgroundColor: 'rgba(255, 99, 132, 0.6)', // Red color with opacity for the bars
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Ratio of Story Points' // Set the name for y-axis
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Days' // Set the name for x-axis
                    }
                }
            }
        }
    });
});
