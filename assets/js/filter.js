// Sources index: filter the list as you type (title and description).
(function () {
  var input = document.getElementById("source-filter");
  if (!input) return;
  var items = Array.prototype.slice.call(document.querySelectorAll("ul.work-list > li"));
  var note = document.createElement("p");
  note.className = "filter-count";
  input.parentNode.parentNode.insertBefore(note, input.parentNode.nextSibling);
  function norm(s) { return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  var texts = items.map(function (li) { return norm(li.textContent); });
  input.addEventListener("input", function () {
    var words = norm(input.value).split(/\s+/).filter(Boolean), shown = 0;
    items.forEach(function (li, i) {
      var ok = words.every(function (w) { return texts[i].indexOf(w) !== -1; });
      li.hidden = !ok; if (ok) shown++;
    });
    note.textContent = words.length ? shown + " of " + items.length + " sources" : "";
  });
})();
