const inputData = {
    labels: [
      "29 Jan 2024", "30 Jan 2024", "31 Jan 2024", "01 Feb 2024", "02 Feb 2024",
      "03 Feb 2024", "04 Feb 2024", "05 Feb 2024", "06 Feb 2024", "07 Feb 2024",
      "08 Feb 2024", "09 Feb 2024", "10 Feb 2024", "11 Feb 2024", "12 Feb 2024",
      "13 Feb 2024", "14 Feb 2024", "15 Feb 2024", "16 Feb 2024", "17 Feb 2024",
      "18 Feb 2024"
    ],
    idealValues: [
      0,10,20,30,40,50,60,70,80
    ],
    existingValues: [
      // Existing values here
    ]
  };
  
  // Sample data for ideal and existing values (replace with your data)
  const idealValues = [
    60, 60, 60, 60, 60, 60, 60, 45.5, 45.5, 45.5,
    45.5, 45.5, 45.5, 51.3, 42.6, 42.6, 42.6, 42.6,
    42.6, 42.6, 42.6
  ];
  
  const existingValues = [
    80, 60, 60, 70, 60, 60, 60, 45.5, 45.5, 45.5,
  45.5, 45.5, 45.5, 51.3, 42.6, 49, 42.6, 42.6,
  42.6, 12.6, 5.6
  ];
  
  const data = {
    labels: inputData.labels,
    datasets: [
      {
        label: 'Ideal Values',
        data: idealValues,
        borderColor: 'green',
        fill: false
      },
      {
        label: 'Existing Values',
        data: existingValues,
        borderColor: 'blue',
        fill: false
      }
    ]
  };
  
  const config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true // Ensure the y-axis starts at 0
          },
          scaleLabel: {
            display: true,
            labelString: 'Value'
          }
        }],
        xAxes: [{
          scaleLabel: {
            display: true,
            labelString: 'Day'
          }
        }]
      }
    }
  };
  
  const ctx = document.getElementById('line-graph').getContext('2d');
  const chart = new Chart(ctx, config);
  