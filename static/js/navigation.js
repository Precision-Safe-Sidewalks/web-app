$(document).ready(() => {
  const { origin, pathname } = window.location;
  const navLinks = $(`nav a[class="nav-item"]`).toArray()
  
  let activeLink = null

  for (navLink of navLinks) {
    const path = $(navLink).prop("href").replace(origin, "")

    if (path === "/" && origin === pathname) {
      activeLink = navLink
      break
    }

    if (pathname.startsWith(path)) {
      activeLink = navLink;
    }
  }

  if (!!activeLink) {
    $(activeLink).addClass("active");
  }
})
