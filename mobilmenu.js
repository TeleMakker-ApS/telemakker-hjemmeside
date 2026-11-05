/* Menuknappen paa mobil. Faelles for forsiden, priser, fagsiderne og
   e-conomic. Knappen saetter klassen menu-aaben paa <header>, og hver side
   bestemmer selv i sin CSS, hvordan menuen ser ud, naar den er aaben. */
(function () {
  var knap = document.querySelector('.menuknap');
  if (!knap) return;
  var hoved = knap.closest('header');
  var nav = hoved.querySelector('nav');

  function saet(aaben) {
    hoved.classList.toggle('menu-aaben', aaben);
    knap.setAttribute('aria-expanded', aaben ? 'true' : 'false');
    knap.setAttribute('aria-label', aaben ? 'Luk menu' : 'Åbn menu');
  }
  function erAaben() { return hoved.classList.contains('menu-aaben'); }

  knap.addEventListener('click', function () { saet(!erAaben()); });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) saet(false);
  });
  document.addEventListener('click', function (e) {
    if (erAaben() && !hoved.contains(e.target)) saet(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && erAaben()) { saet(false); knap.focus(); }
  });
})();
