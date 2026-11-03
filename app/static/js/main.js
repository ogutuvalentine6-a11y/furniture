/* FurnitureHub — advanced interactions (vanilla JS) */
(function () {
  "use strict";

  const $  = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ═══════════════ TOASTS ═══════════════ */
  const ICONS = {
    success: '<svg class="toast-icon" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"/></svg>',
    danger:  '<svg class="toast-icon" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16v.01"/></svg>',
    warning: '<svg class="toast-icon" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17v.01"/></svg>',
    info:    '<svg class="toast-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.01"/></svg>',
  };

  function createToast(category, message) {
    const container = $("#toastContainer");
    if (!container) return;
    const el = document.createElement("div");
    el.className = `toast toast-${category || "info"}`;
    el.innerHTML = `${ICONS[category] || ICONS.info}<div>${message}</div>`;
    container.appendChild(el);
    setTimeout(() => {
      el.classList.add("removing");
      setTimeout(() => el.remove(), 400);
    }, 5000);
  }

  /* ═══════════════ PRELOADER ═══════════════ */
  // Hides when the page is actually ready. Min display 1.4s (so the group
  // names are readable), max 4s (never block the user if something hangs).
  function hidePreloader() {
    const p = $("#preloader");
    if (!p) return;
    const MIN_SHOW = 500;
    const start = performance.now();
    let hidden = false;
    const reallyHide = () => {
      if (hidden) return;
      hidden = true;
      const wait = Math.max(0, MIN_SHOW - (performance.now() - start));
      setTimeout(() => p.classList.add("done"), wait);
    };
    if (document.readyState === "complete" || document.readyState === "interactive") {
      reallyHide();
    } else {
      document.addEventListener("DOMContentLoaded", reallyHide, { once: true });
    }
    setTimeout(reallyHide, 2500);
  }

  /* ═══════════════ SCROLL PROGRESS ═══════════════ */
  function initScrollProgress() {
    const bar = $("#scrollProgress");
    if (!bar) return;
    const update = () => {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  /* ═══════════════ SCROLL REVEAL ═══════════════ */
  function initReveal() {
    const els = $$(".reveal");
    if (!els.length) return;
    if (!("IntersectionObserver" in window)) return;
    // Only NOW hide elements that are below the fold (JS is running).
    els.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.top > window.innerHeight - 100) {
        el.classList.add("reveal-pending");
      }
    });
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.remove("reveal-pending");
          e.target.classList.add("visible");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    els.forEach((el) => io.observe(el));
  }

  /* ═══════════════ ANIMATED COUNTERS ═══════════════ */
  function initCounters() {
    $$("[data-counter]").forEach((el) => {
      const target = parseInt(el.dataset.counter, 10);
      if (!target || target <= 0) { el.textContent = target || 0; return; }
      let current = 0;
      const step = Math.max(1, Math.ceil(target / 45));
      const t = setInterval(() => {
        current += step;
        if (current >= target) { current = target; clearInterval(t); }
        el.textContent = current;
      }, 28);
    });
  }

  /* ═══════════════ BACK TO TOP ═══════════════ */
  function initBackToTop() {
    const btt = $("#backToTop");
    if (!btt) return;
    const toggle = () => {
      if (window.scrollY > 400) btt.classList.remove("opacity-0", "pointer-events-none");
      else btt.classList.add("opacity-0", "pointer-events-none");
    };
    window.addEventListener("scroll", toggle, { passive: true });
    toggle();
    btt.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  /* ═══════════════ TILT CARDS ═══════════════ */
  function initTilt() {
    if (window.matchMedia("(hover: none)").matches) return; // skip mobile
    $$(".tilt").forEach((card) => {
      card.addEventListener("mousemove", (e) => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        card.style.transform = `perspective(900px) rotateX(${(-y * 6).toFixed(2)}deg) rotateY(${(x * 6).toFixed(2)}deg) translateY(-4px)`;
      });
      card.addEventListener("mouseleave", () => {
        card.style.transform = "perspective(900px) rotateX(0) rotateY(0) translateY(0)";
      });
    });
  }

  /* ═══════════════ CART DRAWER ═══════════════ */
  const fmt = (n) => "KSh " + Math.round(Number(n) || 0).toLocaleString();
  function openDrawer() {
    const d = $("#cartDrawer");
    if (!d) return;
    d.classList.add("open");
    document.body.style.overflow = "hidden";
    loadDrawer();
  }
  function closeDrawer() {
    const d = $("#cartDrawer");
    if (!d) return;
    d.classList.remove("open");
    document.body.style.overflow = "";
  }
  async function loadDrawer() {
    const body = $("#drawerBody");
    const count = $("#drawerCount");
    const total = $("#drawerTotal");
    try {
      const res = await fetch("/api/cart", { headers: { Accept: "application/json" } });
      const data = await res.json();
      const items = data.items || [];
      count.textContent = `${data.count || 0} item${data.count === 1 ? "" : "s"}`;
      total.textContent = fmt(data.total);
      if (!items.length) {
        body.innerHTML = `<div class="drawer-empty">
          <svg class="w-12 h-12 mx-auto mb-4 text-grey/40" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M3 4h2l2.5 12h11L21 8H7"/></svg>
          <p class="text-sm">Your cart is empty.</p>
          <a href="/shop" class="inline-block mt-6 bg-charcoal text-ivory px-5 py-2 rounded-full text-sm hover:bg-oak">Browse shop</a>
        </div>`;
        return;
      }
      body.innerHTML = items.map((it) => {
        const img = it.image
          ? `<img src="${it.image.startsWith("http") ? it.image : "/static/" + it.image}" alt="">`
          : `<div class="w-16 h-16 rounded-xl bg-beige shrink-0"></div>`;
        return `<div class="drawer-item">
          ${img}
          <div class="flex-1 min-w-0">
            <a href="/product/${it.slug}" class="font-display text-sm hover:text-oak line-clamp-1">${it.name}</a>
            <div class="text-xs text-grey mt-0.5">${fmt(it.price)} × ${it.quantity}</div>
          </div>
          <div class="text-sm font-semibold">${fmt(it.line_total)}</div>
        </div>`;
      }).join("");
    } catch (err) {
      body.innerHTML = `<div class="drawer-empty">Couldn't load cart. <a href="/cart/" class="underline">Open full cart</a>.</div>`;
    }
  }
  function initCartDrawer() {
    const cartBtn = $("#cartBtn");
    if (cartBtn) {
      cartBtn.addEventListener("click", (e) => { e.preventDefault(); openDrawer(); });
    }
    $$("[data-drawer-close]").forEach((el) => el.addEventListener("click", closeDrawer));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeDrawer();
    });
  }

  /* ═══════════════ COMMAND PALETTE ═══════════════ */
  const CMD_BASE = [
    { label: "Home",              url: "/",              hint: "Landing page" },
    { label: "Shop all furniture",url: "/shop",          hint: "Browse catalogue" },
    { label: "My cart",           url: "/cart/",         hint: "View cart" },
    { label: "Checkout",          url: "/checkout/",     hint: "Place order" },
    { label: "About FurnitureHub",url: "/about",         hint: "Our story" },
    { label: "Contact us",        url: "/contact",       hint: "Support" },
    { label: "Admin — Sign in",   url: "/admin/login",   hint: "Administration" },
    { label: "Admin — Dashboard", url: "/admin/",        hint: "Manage store" },
  ];
  let cmdIndex = 0;
  let cmdResults = CMD_BASE.slice();

  function renderCmd(query) {
    const list = $("#cmdList");
    if (!list) return;
    const q = (query || "").trim().toLowerCase();
    const base = CMD_BASE.filter((c) => !q || c.label.toLowerCase().includes(q));
    // async product search
    if (q) {
      fetch("/api/products?q=" + encodeURIComponent(q))
        .then((r) => r.json())
        .then((products) => {
          const prods = products.slice(0, 5).map((p) => ({
            label: p.name, url: "/product/" + p.slug, hint: fmt(p.price),
          }));
          cmdResults = base.concat(prods);
          paintCmd(cmdResults);
        })
        .catch(() => { cmdResults = base; paintCmd(cmdResults); });
    } else {
      cmdResults = base;
      paintCmd(cmdResults);
    }
  }
  function paintCmd(results) {
    const list = $("#cmdList");
    if (!results.length) {
      list.innerHTML = `<div class="cmd-empty">No results.</div>`;
      return;
    }
    cmdIndex = 0;
    list.innerHTML = results.map((r, i) =>
      `<div class="cmd-item ${i === 0 ? "active" : ""}" data-url="${r.url}">
        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        <span class="cmd-label">${r.label}</span>
        <span class="cmd-hint">${r.hint || ""}</span>
      </div>`
    ).join("");
    list.querySelectorAll(".cmd-item").forEach((el, i) => {
      el.addEventListener("click", () => { window.location.href = el.dataset.url; });
      el.addEventListener("mouseenter", () => { cmdIndex = i; highlight(); });
    });
  }
  function highlight() {
    $$("#cmdList .cmd-item").forEach((el, i) =>
      el.classList.toggle("active", i === cmdIndex)
    );
  }
  function openCmd() {
    const pal = $("#cmdPalette");
    if (!pal) return;
    pal.classList.add("open");
    const input = $("#cmdInput");
    input.value = ""; input.focus();
    renderCmd("");
  }
  function closeCmd() { $("#cmdPalette")?.classList.remove("open"); }
  function initCmd() {
    const pal = $("#cmdPalette");
    if (!pal) return;
    $("#cmdTrigger")?.addEventListener("click", openCmd);
    pal.addEventListener("click", (e) => { if (e.target === pal) closeCmd(); });
    $("#cmdInput").addEventListener("input", (e) => renderCmd(e.target.value));
    pal.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); cmdIndex = Math.min(cmdIndex + 1, cmdResults.length - 1); highlight(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); cmdIndex = Math.max(cmdIndex - 1, 0); highlight(); }
      else if (e.key === "Enter") { e.preventDefault(); const r = cmdResults[cmdIndex]; if (r) window.location.href = r.url; }
    });
    document.addEventListener("keydown", (e) => {
      const k = e.key.toLowerCase();
      if ((e.metaKey || e.ctrlKey) && k === "k") { e.preventDefault(); pal.classList.contains("open") ? closeCmd() : openCmd(); }
      else if (e.key === "Escape") closeCmd();
      else if ((e.metaKey || e.ctrlKey) && e.shiftKey && k === "a") {
        e.preventDefault();
        window.location.href = "/admin/" + ({{ 'true' if current_user.is_authenticated else 'false' }} ? "" : "login");
      }
    });
  }

  /* ═══════════════ NEWSLETTER ═══════════════ */
  function initNewsletter() {
    const form = $("#newsletterForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = form.querySelector('input[name="email"]').value;
      const msg = form.querySelector("[data-msg]");
      try {
        const res = await fetch("/newsletter/subscribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        });
        const data = await res.json();
        if (data.ok) {
          createToast("success", data.message || "Thanks for subscribing!");
          if (msg) msg.textContent = "";
          form.reset();
        } else {
          createToast("danger", data.error || "Something went wrong.");
        }
      } catch {
        createToast("danger", "Network error — please try again.");
      }
    });
  }

  /* ═══════════════ BOOT ═══════════════ */
  document.addEventListener("DOMContentLoaded", () => {
    hidePreloader();

    // Convert flash → toast
    const fc = $("[data-flash-container]");
    if (fc) {
      $$("[data-flash-toast]", fc).forEach((el) => {
        createToast(el.dataset.category, el.dataset.message);
      });
      fc.remove();
    }

    initScrollProgress();
    initReveal();
    initCounters();
    initBackToTop();
    initTilt();
    initCartDrawer();
    initCmd();
    initNewsletter();

    // Confirm destructive forms
    $$("form[data-confirm]").forEach((f) => {
      f.addEventListener("submit", (e) => {
        if (!confirm(f.dataset.confirm)) e.preventDefault();
      });
    });
  });
})();


/* ══════════════════════════════════════════════════════════════
   GROUP 11 PROFILE MODAL
   ══════════════════════════════════════════════════════════════ */
window.openProfile = function(id) {
  var dataEl = document.getElementById('g11Profiles');
  if (!dataEl) return;
  var profiles;
  try { profiles = JSON.parse(dataEl.textContent); } catch(e) { return; }
  var p = profiles[id];
  if (!p) return;

  var contactHTML = '';
  if (p.contact && (p.contact.phone || p.contact.email)) {
    var btns = [];
    if (p.contact.phone) {
      btns.push('<a href="tel:' + p.contact.phone + '" class="profile-contact-btn" style="background:#B58B62;color:#111">📞 ' + p.contact.phone + '</a>');
    }
    if (p.contact.email) {
      btns.push('<a href="mailto:' + p.contact.email + '" class="profile-contact-btn" style="background:#252525;color:#F8F6F1">✉ ' + p.contact.email + '</a>');
    }
    contactHTML = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:1.5rem">' + btns.join('') + '</div>';
  }

  var skillsHTML = (p.skills || []).map(function(s){ return '<span class="profile-skill">' + s + '</span>'; }).join('');
  var founderBadge = p.is_founder ? '<span class="profile-role-badge" style="background:#111;color:#f4d58d">★ Founder</span> ' : '';

  document.getElementById('profileContent').innerHTML =
    '<div class="profile-avatar-lg">' + (p.initials || '') + '</div>' +
    founderBadge +
    '<span class="profile-role-badge">' + p.role + '</span>' +
    '<h2 id="profileName" style="font-family:\'Playfair Display\',serif;font-size:2rem;line-height:1.1;color:#111;margin:0.5rem 0 0.25rem">' + p.name + '</h2>' +
    '<div style="font-family:ui-monospace,monospace;font-size:0.75rem;color:#666;letter-spacing:0.03em">' + p.reg + '</div>' +
    '<p style="color:#333;line-height:1.7;margin-top:1.5rem">' + p.bio + '</p>' +
    '<div style="margin-top:1.75rem"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.15em;color:#8a6844;font-weight:700;margin-bottom:0.5rem">Contribution to FurnitureHub</div>' +
    '<p style="color:#444;line-height:1.6;font-size:0.92rem">' + p.contribution + '</p></div>' +
    '<div style="margin-top:1.75rem"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.15em;color:#8a6844;font-weight:700;margin-bottom:0.5rem">Project Vision</div>' +
    '<p style="color:#444;line-height:1.6;font-size:0.92rem;font-style:italic">"' + p.project_vision + '"</p></div>' +
    '<div style="margin-top:1.75rem"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.15em;color:#8a6844;font-weight:700;margin-bottom:0.5rem">Skills</div><div>' + skillsHTML + '</div></div>' +
    contactHTML;

  document.getElementById('profileModal').classList.add('open');
  document.body.style.overflow = 'hidden';
};

window.closeProfile = function() {
  document.getElementById('profileModal').classList.remove('open');
  document.body.style.overflow = '';
};

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') window.closeProfile();
});
