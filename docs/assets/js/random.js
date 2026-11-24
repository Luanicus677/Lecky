// "Random" links: open a random source page. The list (slug, title,
// subtitle) is written by build.py into assets/js/sources.js.
(function () {
  function pick() {
    var list = window.LECKY_SOURCES || [];
    if (!list.length) return null;
    var here = location.pathname.split("/").pop().replace(/\.html$/, "");
    for (var i = 0; i < 5; i++) {
      var s = list[Math.floor(Math.random() * list.length)];
      if (s[0] !== here) return s;
    }
    return list[0];
  }
  function go(e) {
    var s = pick();
    if (!s) return;               // no list: follow the link to the Sources index
    e.preventDefault();
    location.href = (window.LECKY_ROOT || "") + "ref/" + s[0] + ".html";
  }
  function init() {
    document.querySelectorAll("a.random-source").forEach(function (a) {
      a.addEventListener("click", go);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
