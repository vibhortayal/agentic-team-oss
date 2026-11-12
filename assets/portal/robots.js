// The ten robots, drawn in code. Each has its own colour, head shape, eyes and
// a signature item so people recognise them at a glance.
// Usage: <span class="bot" data-bot="ella"></span>, or Robots.svg("ella").
(function () {
  const INK = "#1d1a22", GLOW = "#7ff3ff";
  const eyesBy = {
    happy: (y) => `<path class="eye" d="M44 ${y + 4} q6 -9 12 0 M64 ${y + 4} q6 -9 12 0" stroke="${GLOW}" stroke-width="4.5" fill="none" stroke-linecap="round"/>`,
    dots: (y) => `<g class="eye"><circle cx="50" cy="${y}" r="5.5" fill="${GLOW}"/><circle cx="70" cy="${y}" r="5.5" fill="${GLOW}"/></g>`,
    tall: (y) => `<g class="eye"><rect x="45" y="${y - 7}" width="9" height="14" rx="4.5" fill="${GLOW}"/><rect x="66" y="${y - 7}" width="9" height="14" rx="4.5" fill="${GLOW}"/></g>`,
    monocle: (y) => `<g class="eye"><circle cx="50" cy="${y}" r="5" fill="${GLOW}"/><circle cx="70" cy="${y}" r="5" fill="${GLOW}"/></g><circle cx="70" cy="${y}" r="10" fill="none" stroke="#ffd35e" stroke-width="3"/><path d="M79 ${y + 4} q6 14 2 26" stroke="#ffd35e" stroke-width="2" fill="none"/>`,
    skeptic: (y) => `<g class="eye"><circle cx="50" cy="${y + 1}" r="5" fill="${GLOW}"/><rect x="63" y="${y - 1}" width="14" height="4" rx="2" fill="${GLOW}"/></g><path d="M43 ${y - 11} l13 3 M63 ${y - 12} l14 -4" stroke="${GLOW}" stroke-width="3" stroke-linecap="round"/>`,
    pixel: (y) => `<g class="eye"><rect x="44" y="${y - 5}" width="11" height="11" fill="${GLOW}"/><rect x="65" y="${y - 5}" width="11" height="11" fill="${GLOW}"/></g>`,
    focused: (y) => `<g class="eye"><path d="M44 ${y - 2} h12 v5 a6 6 0 0 1 -12 0z M64 ${y - 2} h12 v5 a6 6 0 0 1 -12 0z" fill="${GLOW}"/></g>`,
    visor: (y) => `<rect x="40" y="${y - 7}" width="40" height="14" rx="7" fill="${GLOW}" opacity=".25"/><path class="eye" d="M50 ${y} l6 5 l12 -10" stroke="${GLOW}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
    cyclops: (y) => `<circle cx="60" cy="${y}" r="11" fill="none" stroke="${GLOW}" stroke-width="3"/><circle class="eye" cx="60" cy="${y}" r="6" fill="${GLOW}"/>`,
    wink: (y) => `<g class="eye"><circle cx="50" cy="${y}" r="5.5" fill="${GLOW}"/></g><path d="M64 ${y + 1} q6 -6 12 0" stroke="${GLOW}" stroke-width="4" fill="none" stroke-linecap="round"/>`,
  };
  const heads = {
    round: (c) => `<rect x="28" y="22" width="64" height="56" rx="26" fill="${c}"/>`,
    square: (c) => `<rect x="28" y="24" width="64" height="54" rx="12" fill="${c}"/>`,
    wide: (c) => `<rect x="22" y="28" width="76" height="48" rx="18" fill="${c}"/>`,
    tall: (c) => `<rect x="32" y="16" width="56" height="64" rx="24" fill="${c}"/>`,
    hex: (c) => `<path d="M42 22 h36 l16 28 l-16 28 h-36 l-16 -28z" fill="${c}" stroke="${c}" stroke-width="6" stroke-linejoin="round"/>`,
    flat: (c) => `<path d="M26 30 h68 v34 a14 14 0 0 1 -14 14 h-40 a14 14 0 0 1 -14 -14z" fill="${c}"/>`,
    shield: (c) => `<path d="M28 24 h64 v28 c0 16 -14 26 -32 30 c-18 -4 -32 -14 -32 -30z" fill="${c}"/>`,
    dome: (c) => `<circle cx="60" cy="52" r="30" fill="${c}"/>`,
  };
  // Signature items: drawn on top of the body. `top` sits above the head.
  const items = {
    headset: (c) => `<path d="M28 50 a32 32 0 0 1 64 0" stroke="${INK}" stroke-width="5" fill="none"/><rect x="20" y="42" width="12" height="20" rx="5" fill="${INK}"/><rect x="88" y="42" width="12" height="20" rx="5" fill="${INK}"/><path d="M26 60 q0 16 18 16" stroke="${INK}" stroke-width="3" fill="none"/><circle cx="46" cy="76" r="4" fill="${INK}"/>`,
    heart: () => `<g class="ant"><line x1="60" y1="22" x2="60" y2="10" stroke="${INK}" stroke-width="3"/><path d="M60 12 c-6 -8 -16 -2 -10 6 l10 8 l10 -8 c6 -8 -4 -14 -10 -6z" fill="#ff3d8b"/></g>`,
    clipboard: () => `<g class="hold"><rect x="70" y="92" width="30" height="38" rx="4" fill="#fff" stroke="${INK}" stroke-width="3"/><rect x="78" y="88" width="14" height="7" rx="2" fill="${INK}"/><path d="M75 104 l3 3 l5 -6 M75 115 l3 3 l5 -6" stroke="#2e9e5b" stroke-width="2.5" fill="none"/><path d="M87 105 h9 M87 116 h9 M76 125 h20" stroke="${INK}" stroke-width="2"/></g>`,
    star: () => `<g class="ant"><line x1="60" y1="24" x2="60" y2="12" stroke="${INK}" stroke-width="3"/><path d="M60 0 l3.5 7 l7.5 1 l-5.5 5 l1.5 7.5 l-7 -4 l-7 4 l1.5 -7.5 l-5.5 -5 l7.5 -1z" fill="#ffd35e"/></g>`,
    magnifier: () => `<g class="hold"><circle cx="88" cy="100" r="13" fill="#d8f4ff" fill-opacity=".5" stroke="${INK}" stroke-width="4"/><line x1="97" y1="110" x2="108" y2="124" stroke="${INK}" stroke-width="6" stroke-linecap="round"/></g>`,
    ball: () => `<g class="ant"><line x1="60" y1="16" x2="60" y2="6" stroke="${INK}" stroke-width="3"/><circle cx="60" cy="5" r="5" fill="${INK}"/></g>`,
    question: () => `<g class="ant"><path d="M52 10 a8 8 0 1 1 10 8 v4" stroke="${INK}" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="62" cy="27" r="2.6" fill="${INK}"/></g>`,
    redpen: () => `<g class="hold"><rect x="84" y="88" width="8" height="34" rx="3" fill="#e8322b" transform="rotate(28 88 105)"/><path d="M95 120 l4 8 l-8 -3z" fill="${INK}" transform="rotate(0)"/></g>`,
    compass: () => `<g class="ant"><path d="M60 26 l-9 -20 M60 26 l9 -20" stroke="${INK}" stroke-width="3.5" stroke-linecap="round"/><circle cx="60" cy="6" r="4" fill="${INK}"/></g>`,
    blueprint: () => `<g class="hold"><rect x="66" y="98" width="40" height="24" rx="3" fill="#2563eb" stroke="${INK}" stroke-width="3"/><path d="M72 104 h14 v10 h14" stroke="#cfe0ff" stroke-width="2" fill="none"/><circle cx="106" cy="110" r="7" fill="#9fc0ff" stroke="${INK}" stroke-width="3"/></g>`,
    hardhat: () => `<path d="M30 34 a30 26 0 0 1 60 0 z" fill="#ff9f1c" stroke="${INK}" stroke-width="3"/><rect x="24" y="32" width="72" height="8" rx="4" fill="#ff9f1c" stroke="${INK}" stroke-width="3"/><rect x="56" y="12" width="8" height="20" rx="3" fill="#ffc46b"/>`,
    wrench: () => `<g class="hold"><path d="M84 92 a9 9 0 1 0 12 12 l12 14 l6 -6 l-14 -12 a9 9 0 0 0 -12 -12 l6 6 l-4 4z" fill="#b8c2cc" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/></g>`,
    badge: () => `<path d="M60 92 l14 5 v10 c0 9 -6 14 -14 17 c-8 -3 -14 -8 -14 -17 v-10z" fill="#fff" stroke="${INK}" stroke-width="3"/><path d="M54 107 l4 4 l8 -9" stroke="#2e9e5b" stroke-width="3.5" fill="none" stroke-linecap="round"/>`,
    beacon: () => `<g class="ant"><line x1="60" y1="24" x2="60" y2="12" stroke="${INK}" stroke-width="3"/><circle class="blink" cx="60" cy="9" r="6" fill="#5ee08a"/></g>`,
    gauge: () => `<path d="M44 118 a16 16 0 0 1 32 0" fill="#fff" stroke="${INK}" stroke-width="3"/><path d="M48 116 a12 12 0 0 1 6 -9" stroke="#e8322b" stroke-width="3" fill="none"/><path d="M66 107 a12 12 0 0 1 6 9" stroke="#2e9e5b" stroke-width="3" fill="none"/><line class="needle" x1="60" y1="118" x2="60" y2="104" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`,
    dish: () => `<g class="ant"><line x1="60" y1="22" x2="60" y2="12" stroke="${INK}" stroke-width="3"/><path d="M48 4 a12 12 0 0 0 24 0z" fill="#dde3ea" stroke="${INK}" stroke-width="3"/></g>`,
    coin: () => `<g class="ant spin-y"><line x1="60" y1="24" x2="60" y2="16" stroke="${INK}" stroke-width="3"/><circle cx="60" cy="8" r="9" fill="#ffcf3f" stroke="${INK}" stroke-width="3"/><text x="60" y="12.5" text-anchor="middle" font-size="12" font-weight="800" font-family="Inter, sans-serif" fill="${INK}">$</text></g>`,
    calculator: () => `<rect x="47" y="92" width="26" height="32" rx="4" fill="#fff" stroke="${INK}" stroke-width="3"/><rect x="51" y="96" width="18" height="7" rx="1.5" fill="#bdf5c9"/><g fill="${INK}"><circle cx="54" cy="109" r="1.8"/><circle cx="60" cy="109" r="1.8"/><circle cx="66" cy="109" r="1.8"/><circle cx="54" cy="116" r="1.8"/><circle cx="60" cy="116" r="1.8"/><circle cx="66" cy="116" r="1.8"/></g>`,
    gear: () => `<g class="ant"><line x1="60" y1="24" x2="60" y2="16" stroke="${INK}" stroke-width="3"/><g class="spin" style="transform-origin:60px 8px"><circle cx="60" cy="8" r="7" fill="#dde3ea" stroke="${INK}" stroke-width="3" stroke-dasharray="4 2.5"/><circle cx="60" cy="8" r="2.5" fill="${INK}"/></g></g>`,
    rocket: () => `<g class="hold"><path d="M92 128 c-6 -10 -6 -24 4 -36 c10 12 10 26 4 36z" fill="#fff" stroke="${INK}" stroke-width="3"/><circle cx="96" cy="106" r="3.5" fill="#6aa8ff"/><path class="flame" d="M93 130 l3 9 l3 -9z" fill="#ff9f1c"/></g>`,
  };
  const BOTS = {
    ella:  { name: "Ella",  role: "Engagement Lead", c: "#ff6fae", head: "round",  eyes: "happy",   top: ["heart"],  face: ["headset"], hold: [] },
    priya: { name: "Priya", role: "Product Manager", c: "#b28dff", head: "wide",   eyes: "dots",    top: ["star"],   face: [], hold: ["clipboard"] },
    rohan: { name: "Rohan", role: "Researcher",      c: "#6aa8ff", head: "tall",   eyes: "monocle", top: ["ball"],   face: [], hold: ["magnifier"] },
    quinn: { name: "Quinn", role: "Critic",          c: "#ff8f5e", head: "hex",    eyes: "skeptic", top: ["question"], face: [], hold: ["redpen"] },
    arjun: { name: "Arjun", role: "Architect",       c: "#4fd1c5", head: "flat",   eyes: "pixel",   top: ["compass"], face: [], hold: ["blueprint"] },
    ian:   { name: "Ian",   role: "Implementer",     c: "#ffd35e", head: "dome",   eyes: "focused", top: [],          face: ["hardhat"], hold: ["wrench"] },
    vera:  { name: "Vera",  role: "Verifier",        c: "#5ee08a", head: "shield", eyes: "visor",   top: ["beacon"],  face: [], hold: [], chest: ["badge"] },
    max:   { name: "Max",   role: "Evaluator",       c: "#9fb3c8", head: "round",  eyes: "cyclops", top: ["dish"],    face: [], hold: [], chest: ["gauge"] },
    bea:   { name: "Bea",   role: "Budget Analyst",  c: "#ffb45e", head: "square", eyes: "wink",    top: ["coin"],    face: [], hold: [], chest: ["calculator"] },
    otto:  { name: "Otto",  role: "Ops",             c: "#c8e85e", head: "square", eyes: "tall",    top: ["gear"],    face: [], hold: ["rocket"] },
  };
  const shade = (hex, f) => "#" + hex.slice(1).match(/../g).map((h) => Math.min(255, Math.round(parseInt(h, 16) * f)).toString(16).padStart(2, "0")).join("");
  // The builder: you, the person with the idea. A friendly human, not a robot.
  function builder(size, label) {
    return `<svg class="robot robot-you" viewBox="0 -4 120 148" width="${size}" height="${Math.round(size * 148 / 120)}" ${label ? 'role="img" aria-label="You, the builder"' : 'aria-hidden="true"'}>
      <ellipse cx="60" cy="140" rx="30" ry="4" fill="#000" opacity=".18"/>
      <g class="rb">
        <path d="M30 136 v-26 a30 26 0 0 1 60 0 v26z" fill="#3b4a6b"/>
        <path d="M48 86 h24 l-4 14 h-16z" fill="#2e3a55"/>
        <path d="M60 92 v40" stroke="#2e3a55" stroke-width="2"/>
        <g class="arm-wave" style="transform-origin:88px 104px"><path d="M86 104 q16 -6 18 -26" stroke="#3b4a6b" stroke-width="12" fill="none" stroke-linecap="round"/><circle cx="104" cy="74" r="7" fill="#f2c29b"/></g>
        <path d="M34 106 q-8 14 6 24" stroke="#3b4a6b" stroke-width="12" fill="none" stroke-linecap="round"/>
        <g class="mug"><rect x="34" y="118" width="16" height="16" rx="3" fill="#fff" stroke="${INK}" stroke-width="2.5"/><path d="M50 122 a4 4 0 0 1 0 8" stroke="${INK}" stroke-width="2.5" fill="none"/><path class="steam" d="M39 114 q-3 -5 0 -10 M45 114 q-3 -5 0 -10" stroke="#ffffff99" stroke-width="2" fill="none" stroke-linecap="round"/></g>
        <g class="rh">
          <rect x="54" y="72" width="12" height="12" rx="4" fill="#e3ae85"/>
          <circle cx="60" cy="50" r="26" fill="#f2c29b"/>
          <path d="M34 48 c0 -22 18 -30 32 -26 c10 -6 22 4 20 16 c-4 -6 -12 -8 -18 -6 c-10 -4 -26 2 -34 16z" fill="#3a2a20"/>
          <circle cx="35" cy="54" r="5" fill="#e3ae85"/><circle cx="85" cy="54" r="5" fill="#e3ae85"/>
          <g class="eye"><circle cx="50" cy="54" r="3.2" fill="${INK}"/><circle cx="70" cy="54" r="3.2" fill="${INK}"/></g>
          <path d="M44 46 q6 -3 11 0 M65 46 q6 -3 11 0" stroke="#3a2a20" stroke-width="2.5" fill="none" stroke-linecap="round"/>
          <path d="M51 64 q9 8 18 0" stroke="${INK}" stroke-width="3" fill="none" stroke-linecap="round"/>
          <circle cx="44" cy="62" r="4" fill="#ff8f8f" opacity=".5"/><circle cx="76" cy="62" r="4" fill="#ff8f8f" opacity=".5"/>
        </g>
      </g></svg>`;
  }
  function svg(id, { size = 96, label = true } = {}) {
    if (id === "you") return builder(size, label);
    const b = BOTS[id]; if (!b) return "";
    const c = b.c, eyeY = b.head === "tall" ? 46 : b.head === "dome" ? 54 : b.head === "shield" ? 46 : 50;
    const draw = (list) => (list || []).map((k) => items[k](c)).join("");
    return `<svg class="robot robot-${id}" viewBox="0 -4 120 148" width="${size}" height="${Math.round(size * 148 / 120)}" ${label ? `role="img" aria-label="${b.name}, ${b.role}"` : 'aria-hidden="true"'}>
      <ellipse cx="60" cy="140" rx="30" ry="4" fill="#000" opacity=".18"/>
      <g class="rb">
        <rect x="34" y="86" width="52" height="46" rx="16" fill="${shade(c, .82)}"/>
        <rect x="22" y="94" width="12" height="26" rx="6" fill="${shade(c, .7)}"/><rect x="86" y="94" width="12" height="26" rx="6" fill="${shade(c, .7)}"/>
        <rect x="52" y="76" width="16" height="12" fill="${shade(c, .6)}"/>
        ${draw(b.chest)}
        <g class="rh">${draw(b.top)}${heads[b.head](c)}<rect x="38" y="${eyeY - 16}" width="44" height="32" rx="12" fill="${INK}"/>${eyesBy[b.eyes](eyeY)}${draw(b.face)}</g>
        ${draw(b.hold)}
      </g></svg>`;
  }
  const css = `.robot{overflow:visible}.robot .rb{animation:rb-bob 3.2s ease-in-out infinite}.robot .rh{transform-origin:60px 80px;animation:rb-tilt 5s ease-in-out infinite}
  .robot .eye{transform-box:fill-box;transform-origin:center;animation:rb-blink 5.5s infinite}.robot .spin{animation:rb-spin 4s linear infinite}
  .robot .blink{animation:rb-pulse 1.6s ease-in-out infinite}.robot .needle{transform-origin:60px 118px;animation:rb-needle 3s ease-in-out infinite}
  .robot .flame{transform-box:fill-box;transform-origin:top;animation:rb-flame .3s ease-in-out infinite alternate}.robot .spin-y{transform-box:fill-box;transform-origin:center;animation:rb-flip 3s ease-in-out infinite}
  .robot .hold{transform-box:fill-box;transform-origin:left bottom;animation:rb-wave 4s ease-in-out infinite}
  @keyframes rb-bob{50%{transform:translateY(-4px)}}@keyframes rb-tilt{0%,100%{transform:rotate(0)}30%{transform:rotate(-4deg)}60%{transform:rotate(3deg)}}
  @keyframes rb-blink{0%,93%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}@keyframes rb-spin{to{transform:rotate(360deg)}}
  @keyframes rb-pulse{50%{opacity:.35}}@keyframes rb-needle{0%,100%{transform:rotate(-50deg)}50%{transform:rotate(45deg)}}
  .robot .arm-wave{animation:rb-hi 2.4s ease-in-out infinite}.robot .steam{animation:rb-steam 2s ease-in-out infinite}
  @keyframes rb-hi{0%,60%,100%{transform:rotate(0)}70%,90%{transform:rotate(-14deg)}80%{transform:rotate(10deg)}}@keyframes rb-steam{0%{opacity:0;transform:translateY(3px)}50%{opacity:1}100%{opacity:0;transform:translateY(-4px)}}
  @keyframes rb-flame{to{transform:scaleY(1.6)}}@keyframes rb-flip{0%,70%,100%{transform:scaleX(1)}85%{transform:scaleX(-1)}}@keyframes rb-wave{50%{transform:rotate(-6deg)}}
  @media (prefers-reduced-motion: reduce){.robot *{animation:none!important}}`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  function fill(root = document) {
    root.querySelectorAll("[data-bot]").forEach((el, i) => {
      if (el.dataset.drawn) return;
      el.innerHTML = svg(el.dataset.bot, { size: +(el.dataset.size || 96), label: el.dataset.label !== "no" });
      el.dataset.drawn = 1;
      const r = el.querySelector(".rb"); if (r) r.style.animationDelay = (-(i * .37) % 3.2) + "s";
    });
  }
  window.Robots = { svg, fill, list: BOTS, dataUrl: (id) => "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg(id).replace('class="robot', 'xmlns="http://www.w3.org/2000/svg" class="robot')) };
  if (document.readyState !== "loading") fill(); else document.addEventListener("DOMContentLoaded", () => fill());
})();
