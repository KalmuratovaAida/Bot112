
document.querySelectorAll(".nav-link").forEach((element) => {
    element.addEventListener("click", () => {
        document.body.classList.add('fade-out')
        setTimeout(() => {document.body.classList.add('non-visible')}, 300)
    })
})

$(document).ready(() => {
    document.body.classList.add('fade-in')
    document.body.classList.remove('non-visible')
})

toastElements = document.getElementsByClassName('toast')
for (let toast of toastElements) {
    new bootstrap.Toast(toast).show()
}

