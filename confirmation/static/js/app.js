// Menu hamburger (téléphone)
const btn = document.getElementById("menu-btn");
const menu = document.getElementById("mobile-menu");
const iconOpen = document.getElementById("icon-open");
const iconClose = document.getElementById("icon-close");

if (btn && menu) {
  btn.addEventListener("click", () => {
    const ouvert = menu.classList.toggle("hidden") === false;
    iconOpen.classList.toggle("hidden", ouvert);
    iconClose.classList.toggle("hidden", !ouvert);
    btn.setAttribute("aria-expanded", ouvert);
    btn.setAttribute("aria-label", ouvert ? "Fermer le menu" : "Ouvrir le menu");
  });
}

// Numéro de table du BAC : majuscules et tirets automatiques (215-AA00-0000)
document.querySelectorAll('[data-masque="numero-table"]').forEach((champ) => {
  champ.addEventListener("input", () => {
    const brut = champ.value.toUpperCase().replace(/[^0-9A-Z]/g, "").slice(0, 11);
    champ.value = [brut.slice(0, 3), brut.slice(3, 7), brut.slice(7)]
      .filter(Boolean)
      .join("-");
  });
});
