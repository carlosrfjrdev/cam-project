/* DS CAM — Showcase nav (vanilla JS, file:// friendly).
   Renderiza sidebar + hamburguer. Marca link ativo pela URL. */
(function () {
  var NAV = [
    { label: "Visão geral", items: [["Início", "index.html"]] },
    { label: "Fundamentos", items: [
      ["Colors", "colors.html"],
      ["Branding", "branding.html"],
      ["Tokens", "tokens.html"],
      ["Shadows & Elevation", "shadows.html"],
      ["Grids & Spacing", "grids.html"],
    ]},
    { label: "Forms", items: [
      ["TextField", "text-fields.html"],
      ["Chip", "chips.html"],
      ["Checkbox", "checkbox.html"],
      ["Select", "select.html"],
      ["Radio", "radio.html"],
      ["ToggleButtonGroup", "toggle-button-group.html"],
      ["Switch", "switch.html"],
      ["Button", "buttons.html"],
    ]},
    { label: "Data", items: [
      ["Table", "table.html"],
      ["Pagination", "pagination.html"],
    ]},
    { label: "Panels", items: [
      ["Card", "card.html"],
      ["Accordion", "accordion.html"],
      ["Divider", "divider.html"],
      ["Stepper", "stepper.html"],
      ["Tabs", "tabs.html"],
      ["Paper", "paper.html"],
      ["Dialog", "dialog.html"],
      ["Drawer", "drawer.html"],
      ["Tooltip", "tooltip.html"],
    ]},
    { label: "Messages", items: [
      ["Snackbar", "snackbar.html"],
      ["Alert", "alert.html"],
      ["Badge", "badge.html"],
    ]},
  ];

  var cur = location.pathname.split("/").pop() || "index.html";

  var html = '<div class="brand"><span class="c">C</span><span class="a">a</span>' +
             '<span class="m">M</span><small>DS Showcase</small></div><div class="nav">';
  NAV.forEach(function (g) {
    html += '<div class="nav-group"><div class="label">' + g.label + '</div>';
    g.items.forEach(function (it) {
      var active = (it[1] === cur) ? ' class="active"' : '';
      html += '<a href="' + it[1] + '"' + active + '>' + it[0] + '</a>';
    });
    html += '</div>';
  });
  html += '</div>';

  var aside = document.createElement("aside");
  aside.className = "sidebar";
  aside.innerHTML = html;

  var scrim = document.createElement("div");
  scrim.className = "scrim";
  scrim.addEventListener("click", function () { document.body.classList.remove("nav-open"); });

  document.addEventListener("DOMContentLoaded", function () {
    var app = document.querySelector(".app");
    app.insertBefore(aside, app.firstChild);
    document.body.appendChild(scrim);
    var burger = document.querySelector(".hamburger");
    if (burger) burger.addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
    });
  });
})();
