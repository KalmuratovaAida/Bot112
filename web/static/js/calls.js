moment.locale('ru')

let table = null

$(document).ready(() => {
    table = $("#callsTable").DataTable({
        "ajax": "api/all_calls",
        "columns": [
            {data: "id"},
            {
                data: "processed",
                render: (data, type, row) => {
                    return `<input class="form-check-input" type="checkbox" id="flexCheckChecked" ${data ? 'checked' : NaN} disabled>`
                }
            },
            {
                data: "number",
                render: (data, type, row) => {
                    return data.replace('<sip:', '').replace('>', '')
                }
            },
            {data: "incident"},
            {data: "address"},
            {
                data: "datetime",
                render: (data, type, row) => {
                    return moment(data).format('MM.DD.YYYY, H:mm:ss')
                }
            },
            {
                data: null,
                render: (data, type, row) => {
                    return `<button class="btn btn-info" data-bs-toggle="modal" data-bs-target="#infoModal" data-call-id="${data.id}"><i class="fa fa-info-circle text-white"></i></button>
                            <button class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#deleteModal" data-call-id="${data.id}"><i class="fa fa-times text-white"></i></button>`
                }
            }
        ],
        "order": [[0, "desc"]],
        "responsive": true,
        "fixedHeader": true,
        "lengthChange": false,
        "pageLength": 20,
        "language": {
            "zeroRecords": "Не найдено",
            "info": "Страница _PAGE_ из _PAGES_",
            "infoEmpty": "Нет доступных запросов",
            "infoFiltered": "(Отфильтровано из всех _MAX_ запросов)",
            "search": "Поиск ",
            "paginate": {
                "first": "Первая",
                "last": "Последняя",
                "next": "Вперёд",
                "previous": "Назад"
            }
        }
    })
})

$('#deleteBtn').on('click', (event) => {
    const callId = event.target.getAttribute('data-call-id')
    $.ajax(`/api/delete_call?cid=${callId}`).then((r) => {
        table.ajax.reload(null, false)
    })
})

setInterval(function () {
    table.ajax.reload(null, false);
}, 15000);


$('#infoModal').on('show.bs.modal', (event) => {
    const callId = event.relatedTarget.getAttribute('data-call-id')
    $.ajax(`/api/call?cid=${callId}`).then((r) => {
        let chat_log = r.data.transcription.split('\n').map((value) => {
            return `• ${value}\n `
        }).join(' ')
        $('#info').text(chat_log)
        $('#incident').text(r.data.incident)
        $('#datetime').text(moment(r.data.datetime).format('MM.DD.YYYY, h:mm:ss'))
        $('#address').text(r.data.address)
        $('#caller').text(r.data.number)
        $('#proceedCheckBox').prop('checked', r.data.processed)
        $('audio').attr('src', `/api/call_mp3?cid=${r.data.id}`)
        if (r.data.point) {
            $('#map').attr('src', `https://static.maps.2gis.com/1.0?s=768x768&c=${r.data.point}&z=17&pt=${r.data.point}`)
        } else {
            $('#map').attr('src', `/static/nomap.jpg`)
        }

        $('#saveButton').on('click', () => {
            let checked = $('#proceedCheckBox').is(':checked')
            if (checked !== r.data.processed) {
                $.ajax(`/api/update_call?cid=${r.data.id}&proceed=${checked ? 1 : 0}`).then((r) => {
                    table.ajax.reload(null, false)
                })
            }
        })

    })

}).on('hide.bs.modal', () => {
    $('#info').text('Загрузка...')
})


$('#deleteModal').on('show.bs.modal', (event) => {
    const callId = event.relatedTarget.getAttribute('data-call-id')
    $('#deleteBtn').attr('data-call-id', callId)
})
