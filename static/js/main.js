document.addEventListener('DOMContentLoaded', function () {
  $(document).ready(function () {
    $('.nav .nav-link').each(function () {
      let link = this.href.split('/')[4]
      let mass_word = window.location.pathname.split('/')[2]
      console.log(link, mass_word)
      if (mass_word == link) {
        $(this).addClass('active')
      }
    })
  })
})

// window.addEventListener('DOMContentLoaded', function () {
//   $('.nav a').each(function () {
//     let location =
//       window.location.protocol +
//       '//' +
//       window.location.host +
//       window.location.pathname
//     let link = this.href
//     console.log(link)
//     console.log(location)
//     if (location == link) {
//       $(this).parent().addClass('active')
//     }
//   })
// })
