"use strict";

// Hide images the source server could not deliver; the typed placeholder stays visible.
function markBroken(img) {
  img.classList.add("is-broken");
}
document.querySelectorAll("img[data-fallback]").forEach((img) => {
  if (img.complete && img.naturalWidth === 0) markBroken(img);
  img.addEventListener("error", () => markBroken(img));
});

// On narrow screens the filters start collapsed, so results come first.
if (window.matchMedia("(max-width: 900px)").matches) {
  document.querySelectorAll("details.facets-toggle").forEach((details) => (details.open = false));
}

// Sort and page-size selects submit their form.
document.querySelectorAll("select[data-autosubmit]").forEach((select) => {
  select.addEventListener("change", () => select.form.submit());
});

// Copy buttons.
document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = document.querySelector(button.dataset.copy);
    if (!target) return;
    try {
      await navigator.clipboard.writeText(target.textContent.trim());
      const label = button.textContent;
      button.textContent = button.dataset.copied;
      setTimeout(() => (button.textContent = label), 1500);
    } catch (error) {
      window.getSelection().selectAllChildren(target);
    }
  });
});

// Entity autocomplete (ТЗ 7.4): names in every language lead to entity pages.
document.querySelectorAll("input[data-suggest]").forEach((input) => {
  const list = document.getElementById(input.getAttribute("aria-controls"));
  let timer = null;
  let active = -1;
  let controller = null;

  const close = () => {
    list.hidden = true;
    list.innerHTML = "";
    active = -1;
    input.setAttribute("aria-expanded", "false");
  };

  const highlight = (index) => {
    const links = list.querySelectorAll("a");
    links.forEach((link, i) => link.setAttribute("aria-selected", String(i === index)));
    active = index;
  };

  input.addEventListener("input", () => {
    clearTimeout(timer);
    const value = input.value.trim();
    if (value.length < 2) return close();
    timer = setTimeout(async () => {
      if (controller) controller.abort();
      controller = new AbortController();
      try {
        const response = await fetch(`${input.dataset.suggest}&q=${encodeURIComponent(value)}`, { signal: controller.signal });
        if (!response.ok) return close();
        const items = await response.json();
        if (!items.length) return close();
        list.innerHTML = "";
        items.forEach((item) => {
          const li = document.createElement("li");
          li.setAttribute("role", "option");
          const a = document.createElement("a");
          a.href = input.dataset.entityUrl + encodeURIComponent(item.id);
          const label = document.createElement("span");
          label.textContent = item.label;
          label.dir = "auto";
          const count = document.createElement("small");
          count.textContent = item.count.toLocaleString(document.documentElement.lang);
          a.append(label, count);
          li.append(a);
          list.append(li);
        });
        list.hidden = false;
        input.setAttribute("aria-expanded", "true");
      } catch (error) {
        if (error.name !== "AbortError") close();
      }
    }, 150);
  });

  input.addEventListener("keydown", (event) => {
    const links = list.querySelectorAll("a");
    if (list.hidden || !links.length) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      highlight((active + 1) % links.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      highlight((active - 1 + links.length) % links.length);
    } else if (event.key === "Enter" && active >= 0) {
      event.preventDefault();
      window.location.href = links[active].href;
    } else if (event.key === "Escape") {
      close();
    }
  });

  document.addEventListener("click", (event) => {
    if (!input.parentElement.contains(event.target)) close();
  });
});

// Image viewer: a plain image first, deep zoom with OpenSeadragon once it has loaded.
document.querySelectorAll("[data-viewer]").forEach((stage) => {
  const images = JSON.parse(stage.dataset.images);
  const plain = stage.querySelector(".viewer-image");
  const fallback = stage.querySelector(".viewer-fallback");
  const thumbs = stage.parentElement.querySelectorAll(".viewer-thumbs button");
  let viewer = null;
  let current = 0;

  const fail = () => {
    plain.hidden = true;
    fallback.hidden = false;
  };
  const show = (index) => {
    current = index;
    thumbs.forEach((button, i) => (i === index ? button.setAttribute("aria-current", "true") : button.removeAttribute("aria-current")));
    fallback.hidden = true;
    if (viewer) {
      viewer.goToPage(index);
    } else {
      plain.hidden = false;
      plain.src = images[index];
    }
  };
  const upgrade = () => {
    if (viewer || !window.OpenSeadragon || plain.naturalWidth === 0) return;
    viewer = window.OpenSeadragon({
      element: stage,
      prefixUrl: stage.dataset.osdPrefix,
      tileSources: images.map((url) => ({ type: "image", url })),
      sequenceMode: images.length > 1,
      initialPage: current,
      showNavigator: false,
      showSequenceControl: false,
      gestureSettingsMouse: { clickToZoom: false },
    });
    viewer.addHandler("open", () => (plain.hidden = true));
    viewer.addHandler("open-failed", fail);
  };

  // A source server that does not answer keeps the request open for a long time.
  const slow = setTimeout(() => {
    if (plain.naturalWidth === 0) fallback.hidden = false;
  }, 8000);
  plain.addEventListener("error", fail);
  plain.addEventListener("load", () => {
    clearTimeout(slow);
    fallback.hidden = true;
    if (window.OpenSeadragon) upgrade();
    else window.addEventListener("load", upgrade, { once: true });
  });
  if (plain.complete) {
    if (plain.naturalWidth === 0) fail();
    else window.addEventListener("load", upgrade, { once: true });
  }
  thumbs.forEach((button) => button.addEventListener("click", () => show(Number(button.dataset.index))));
});
