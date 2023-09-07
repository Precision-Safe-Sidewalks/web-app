$(document).ready(() => {
  $(`div[class="dialog"]`).each((_, dialog) => {
    const controlId = $(dialog).data("control")
    const control = document.getElementById(controlId)
      
    // If the control button is clicked, toggle the "open" class to
    // control the state of the dialog menu
    $(control).on("click", () => {
      $(dialog).is(":hidden") ? $(dialog).addClass("open") : $(dialog).removeClass("open")
    })

    // If the background scrim is clicked (i.e. "dialog"), then close
    // the dialog by removing the "open" class
    $(dialog).on("click", (event) => {
      if ($(event.target).is(dialog)) {
        $(dialog).removeClass("open")
      }
    })
  })
})
