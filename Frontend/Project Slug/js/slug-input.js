const alertPlaceholder = document.getElementById('liveAlertContainer');

const appendAlert = (message, type) => {
    const wrapper = document.createElement('div')
    const id = Math.random();
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert" id='${id}'>`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)

    const bsAlert = new bootstrap.Alert(`#${id}`)
    setTimeout(() => bsAlert.close(), 3000);
}