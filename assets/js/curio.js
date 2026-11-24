// Home page: show three random items from the Cabinet of Curiosities,
// with a button to draw three more. The static items in the page are the
// fallback if the fetch fails.
(function () {
  var box = document.getElementById("curio-box");
  if (!box || !window.fetch || !window.DOMParser) return;
  var list = box.querySelector("ul");
  var btn = box.querySelector(".curio-shuffle");
  var items = [], pos = 0;

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function draw() {
    if (items.length < 3) return;
    if (pos + 3 > items.length) { shuffle(items); pos = 0; }
    list.innerHTML = "";
    for (var k = 0; k < 3; k++) list.appendChild(items[pos + k].cloneNode(true));
    pos += 3;
    if (window.leckyBindPopups) window.leckyBindPopups(list);
  }

  fetch((window.LECKY_ROOT || "") + "curiosities.html")
    .then(function (r) { return r.ok ? r.text() : Promise.reject(); })
    .then(function (html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      items = shuffle(Array.prototype.slice.call(doc.querySelectorAll("ul.curiosities > li")));
      if (items.length < 3) return;
      draw();
      if (btn) { btn.hidden = false; btn.addEventListener("click", draw); }
    })
    .catch(function () {});
})();
