const ctx = document.getElementById('chart').getContext('2d')
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: []
    },
    options: {
        responsive: true,
        scales: {
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Звонки'
                },
                suggestedMin: 0,
                suggestedMax: 10
            }
        },
    }
})

function refreshData(chart) {
    $.ajax('/api/count_by_date').then(resp => {
        let data = resp['data']
        chart.data.labels = []
        chart.data.datasets = []
        data['datasets'].forEach(value => {
            chart.data.datasets.push({
                label: value['dataName'],
                data: value['data'],
                backgroundColor: '#' + Math.floor(Math.random() * 16777215).toString(16),
                borderWidth: 1,
                fill: true
            })
        })
        chart.update()
    })
}

refreshData(chart)

$('#refreshBtn').on('click', () => {
    window.location.reload()
})

$('#excelExportBtn').on('click', () => {
    window.location.assign('api/export/excel')
})

$('#wordExportBtn').on('click', () => {
    const img = chart.toBase64Image().split(',')[1]

    $.ajax({
        url: "api/export/word",
        type: "POST",
        data: {
            image: img,
        },
        success: res => {
            // $.ajax({url: 'api/export/word', type: 'GET'})
            // $.get('api/export/word')
            window.location.assign('api/export/word')
        },
        error: res => {
            alert('Произошла ошибка!')
        }
    })
})
