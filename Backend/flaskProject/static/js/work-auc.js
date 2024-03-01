const partial_work_auc_chart_config = {
    type: 'bar',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Partial Work AUC Delta',
                data: [],
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Date',
                    font: { size: 15 },
                },
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Delta',
                    font: { size: 15 },
                },

            }
        },
    }
}

const total_work_auc_chart_config = {
    type: 'bar',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Total Work AUC Delta',
                data: [],
                borderColor: '#ff8fa7',
                backgroundColor: '#ff8fa7',
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Date',
                    font: { size: 15 },
                },
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Delta',
                    font: { size: 15 },
                },

            }
        },
    }
}

$(function () {
    $.ajax({
        url: '/partial-work-auc-data',
        type: 'GET',
        success: function (response) {
            partial_work_auc_chart_config.data.labels = response.x_axis.map(date => {
                const dateObj = new Date(date);
                return `${dateObj.getDate()} ${dateObj.toLocaleDateString('default', { month: 'short' })}`
            });

            partial_work_auc_chart_config.data.datasets[0].data = response.work_auc_delta;

            const partial_work_auc_chart = document.getElementById('partial_work_auc_chart').getContext('2d');
            new Chart(partial_work_auc_chart, partial_work_auc_chart_config);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest.status)
            console.log(textStatus)
        }
    })

    $.ajax({
        url: '/total-work-auc-data',
        type: 'GET',
        success: function (response) {
            total_work_auc_chart_config.data.labels = response.x_axis.map(date => {
                const dateObj = new Date(date);
                return `${dateObj.getDate()} ${dateObj.toLocaleDateString('default', { month: 'short' })}`
            });

            total_work_auc_chart_config.data.datasets[0].data = response.work_auc_delta;

            const total_work_auc_chart = document.getElementById('total_work_auc_chart').getContext('2d');
            new Chart(total_work_auc_chart, total_work_auc_chart_config);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest.status)
            console.log(textStatus)
        }
    })
})

