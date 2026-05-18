/* ── Estado global ───────────────────────────────────────────────────────── */
const state = {
  tipo:       "",
  presupuesto:"",
  continente: "",
  busqueda:   "",
  chatHistory:[],
};

/* ── Inicialización ──────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  loadStats();
  loadDestinos();
  initFilters();
  initSearch();
  initChatbot();
  initModal();
});

/* ── Stats ───────────────────────────────────────────────────────────────── */
async function loadStats() {
  try {
    const d = await fetch("/api/stats").then(r => r.json());
    setEl("stat-destinos",    d.destinos);
    setEl("stat-paquetes",    d.paquetes);
    setEl("stat-valoraciones",d.valoraciones);
  } catch (_) {}
}

/* ── Carga y renderizado de destinos ─────────────────────────────────────── */
async function loadDestinos() {
  const grid = document.getElementById("destinations-grid");
  showSkeletons(grid, 6);

  const params = new URLSearchParams();
  if (state.tipo)       params.set("tipo",       state.tipo);
  if (state.presupuesto)params.set("presupuesto",state.presupuesto);
  if (state.continente) params.set("continente", state.continente);
  if (state.busqueda)   params.set("busqueda",   state.busqueda);

  const destinos = await fetch("/api/destinos?" + params).then(r => r.json());

  setEl("count-badge", destinos.length + " destino" + (destinos.length !== 1 ? "s" : ""));

  grid.innerHTML = "";
  if (!destinos.length) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="icon">🔍</div>
        <p>No encontramos destinos con esos filtros.<br>Prueba a cambiar los criterios de búsqueda.</p>
      </div>`;
    return;
  }
  destinos.forEach(d => grid.appendChild(buildCard(d)));
}

function buildCard(d) {
  const div = document.createElement("div");
  div.className = "card";
  div.innerHTML = `
    <div class="card-img-wrap">
      <img src="${d.imagen_url}" alt="${d.nombre}"
           onerror="this.src='https://picsum.photos/seed/${d.id}/600/400'">
      <span class="card-badge badge-${d.tipo}">${emoji(d.tipo)} ${cap(d.tipo)}</span>
      ${d.valoracion >= 4.8 ? '<span class="card-featured">⭐ Top rated</span>' : ""}
    </div>
    <div class="card-body">
      <p class="card-title">${d.nombre}</p>
      <p class="card-country">📍 ${d.pais}</p>
      <div>
        <span class="stars">${stars(d.valoracion)}</span>
        <span class="stars-count">${d.valoracion.toFixed(1)}</span>
      </div>
    </div>
    <div class="card-footer">
      <div class="card-price">Desde <strong>${Math.round(d.precio_desde)}€</strong></div>
      <button class="btn-card">Ver más</button>
    </div>`;
  div.addEventListener("click", () => openModal(d.id));
  return div;
}

/* ── Filtros ─────────────────────────────────────────────────────────────── */
function initFilters() {
  // Tipo pills del hero
  document.querySelectorAll(".pill").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".pill").forEach(b => b.classList.remove("active"));
      const v = btn.dataset.tipo;
      if (state.tipo === v) {
        state.tipo = "";
      } else {
        btn.classList.add("active");
        state.tipo = v;
      }
      // sync sidebar radio
      document.querySelectorAll('input[name="tipo"]').forEach(r => {
        r.checked = r.value === state.tipo;
      });
      loadDestinos();
    });
  });

  // Sidebar radios
  document.querySelectorAll('input[name="tipo"]').forEach(r =>
    r.addEventListener("change", () => {
      state.tipo = r.value;
      document.querySelectorAll(".pill").forEach(b => {
        b.classList.toggle("active", b.dataset.tipo === state.tipo);
      });
      loadDestinos();
    })
  );

  document.querySelectorAll('input[name="presupuesto"]').forEach(r =>
    r.addEventListener("change", () => { state.presupuesto = r.value; loadDestinos(); })
  );

  document.querySelectorAll('input[name="continente"]').forEach(r =>
    r.addEventListener("change", () => { state.continente = r.value; loadDestinos(); })
  );

  document.getElementById("btn-reset")?.addEventListener("click", resetFilters);
}

function resetFilters() {
  state.tipo = state.presupuesto = state.continente = state.busqueda = "";
  document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
  document.querySelectorAll(".pill").forEach(b => b.classList.remove("active"));
  document.getElementById("search-input").value = "";
  loadDestinos();
}

/* ── Búsqueda ────────────────────────────────────────────────────────────── */
function initSearch() {
  const input = document.getElementById("search-input");
  const btn   = document.getElementById("search-btn");
  let timer;

  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => { state.busqueda = input.value.trim(); loadDestinos(); }, 400);
  });

  input.addEventListener("keydown", e => {
    if (e.key === "Enter") { state.busqueda = input.value.trim(); loadDestinos(); }
  });

  btn.addEventListener("click", () => { state.busqueda = input.value.trim(); loadDestinos(); });
}

/* ── Modal de detalle ────────────────────────────────────────────────────── */
let currentDestinoId = null;
let selectedRating   = 0;

function initModal() {
  document.getElementById("modal-overlay").addEventListener("click", e => {
    if (e.target === document.getElementById("modal-overlay")) closeModal();
  });
  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

  // Tabs
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("panel-" + btn.dataset.tab).classList.add("active");
    });
  });

  // Estrellas de reseña
  document.querySelectorAll(".star-label").forEach(lbl => {
    lbl.addEventListener("click", () => {
      selectedRating = +lbl.dataset.val;
      highlightStars(selectedRating);
    });
  });

  // Enviar reseña
  document.getElementById("btn-submit-review").addEventListener("click", submitReview);
}

async function openModal(id) {
  currentDestinoId = id;
  selectedRating = 0;
  document.getElementById("modal-overlay").classList.add("open");
  document.body.style.overflow = "hidden";

  const data = await fetch("/api/destinos/" + id).then(r => r.json());
  const d = data.destino;

  document.getElementById("modal-img").src = d.imagen_url;
  document.getElementById("modal-img").onerror = function() {
    this.src = "https://picsum.photos/seed/" + id + "/800/400";
  };
  document.getElementById("modal-title").textContent   = d.nombre;
  document.getElementById("modal-country").textContent = "📍 " + d.pais + "  " + stars(d.valoracion) + "  " + d.valoracion.toFixed(1);
  document.getElementById("modal-desc").textContent    = d.descripcion;
  document.getElementById("modal-clima").textContent   = d.clima || "—";
  document.getElementById("modal-epoca").textContent   = d.mejor_epoca || "—";
  document.getElementById("modal-precio").textContent  = "Desde " + Math.round(d.precio_desde) + "€";

  renderActividades(d.actividades);
  renderPaquetes(data.paquetes);
  renderHoteles(data.hoteles);
  renderValoraciones(data.valoraciones);

  // reset tabs
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelector('.tab-btn[data-tab="paquetes"]').classList.add("active");
  document.getElementById("panel-paquetes").classList.add("active");

  // reset review form
  highlightStars(0);
  document.getElementById("review-text").value = "";
}

function closeModal() {
  document.getElementById("modal-overlay").classList.remove("open");
  document.body.style.overflow = "";
}

function renderActividades(acts) {
  const wrap = document.getElementById("modal-actividades");
  wrap.innerHTML = "";
  if (!acts) return;
  acts.split(",").forEach(a => {
    const s = document.createElement("span");
    s.className = "pkg-tag";
    s.textContent = a.trim();
    wrap.appendChild(s);
  });
}

function renderPaquetes(paquetes) {
  const wrap = document.getElementById("panel-paquetes");
  wrap.innerHTML = "";
  if (!paquetes.length) {
    wrap.innerHTML = "<p style='color:#94a3b8;text-align:center;padding:20px'>Sin paquetes disponibles actualmente.</p>";
    return;
  }
  paquetes.forEach(p => {
    const tags = [
      p.incluye_vuelo ? "✈️ Vuelo incl." : "",
      p.incluye_hotel ? "🏨 Hotel incl." : "",
      "👥 " + p.num_viajeros + " viajeros",
      "📅 " + p.duracion_dias + " días",
    ].filter(Boolean);

    wrap.innerHTML += `
      <div class="package-card">
        <div>
          <p class="pkg-name">${p.nombre}</p>
          <p class="pkg-desc">${p.descripcion}</p>
          <div class="pkg-tags">${tags.map(t => `<span class="pkg-tag">${t}</span>`).join("")}</div>
        </div>
        <div class="pkg-price">
          <span class="price-big">${Math.round(p.precio)}€</span>
          <span class="price-sub">por persona</span>
          <button class="btn-reservar" onclick="toast('¡Reserva iniciada! Te contactaremos pronto.')">Reservar</button>
        </div>
      </div>`;
  });
}

function renderHoteles(hoteles) {
  const wrap = document.getElementById("panel-hoteles");
  wrap.innerHTML = "";
  if (!hoteles.length) {
    wrap.innerHTML = "<p style='color:#94a3b8;text-align:center;padding:20px'>Sin hoteles registrados.</p>";
    return;
  }
  hoteles.forEach(h => {
    wrap.innerHTML += `
      <div class="hotel-item">
        <div style="flex:1">
          <div class="hotel-stars">${"★".repeat(h.categoria)}${"☆".repeat(5 - h.categoria)}</div>
          <p class="hotel-name">${h.nombre}</p>
          <p class="hotel-desc">${h.descripcion}</p>
          <p class="hotel-services">🛎️ ${h.servicios.replace(/,/g, " · ")}</p>
        </div>
        <div class="hotel-price-col">
          <div class="hotel-price-big">${Math.round(h.precio_noche)}€</div>
          <div class="hotel-price-sub">/ noche</div>
        </div>
      </div>`;
  });
}

function renderValoraciones(vals) {
  const wrap = document.getElementById("panel-valoraciones");
  wrap.innerHTML = "";
  if (!vals.length) {
    wrap.innerHTML = "<p style='color:#94a3b8;text-align:center;padding:12px'>Sé el primero en valorar este destino.</p>";
  } else {
    vals.forEach(v => {
      wrap.innerHTML += `
        <div class="review-item">
          <div class="review-header">
            <span class="review-author">${v.usuario_nombre} &nbsp;<span class="stars">${stars(v.puntuacion)}</span></span>
            <span class="review-date">${v.fecha}</span>
          </div>
          <p class="review-text">${v.comentario}</p>
        </div>`;
    });
  }
  // Keep the form
  wrap.innerHTML += `
    <div class="review-form">
      <h4>✍️ Deja tu valoración</h4>
      <div class="star-input" id="star-input">
        ${[5,4,3,2,1].map(n =>
          `<label class="star-label" data-val="${n}" title="${n} estrellas">★</label>`
        ).join("")}
      </div>
      <textarea id="review-text" placeholder="Cuéntanos tu experiencia..."></textarea>
      <button class="btn-submit-review" id="btn-submit-review">Enviar valoración</button>
    </div>`;

  document.querySelectorAll(".star-label").forEach(lbl => {
    lbl.addEventListener("click", () => {
      selectedRating = +lbl.dataset.val;
      highlightStars(selectedRating);
    });
  });
  document.getElementById("btn-submit-review").addEventListener("click", submitReview);
}

function highlightStars(rating) {
  document.querySelectorAll(".star-label").forEach(lbl => {
    lbl.style.color = +lbl.dataset.val <= rating ? "#f59e0b" : "#cbd5e1";
  });
}

async function submitReview() {
  const comentario = document.getElementById("review-text")?.value.trim();
  if (!selectedRating) { toast("Elige una puntuación (1-5 estrellas)"); return; }
  if (!comentario)     { toast("Escribe un comentario antes de enviar"); return; }

  const res = await fetch("/api/valoraciones", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ destino_id: currentDestinoId, puntuacion: selectedRating, comentario }),
  }).then(r => r.json());

  if (res.ok) {
    toast("¡Gracias por tu valoración! ⭐");
    openModal(currentDestinoId);
    loadDestinos();
  } else {
    toast("Error al enviar. Inténtalo de nuevo.");
  }
}

/* ── Chatbot ─────────────────────────────────────────────────────────────── */
function initChatbot() {
  const toggle = document.getElementById("chatbot-toggle");
  const panel  = document.getElementById("chatbot-panel");
  const closeB = document.getElementById("chatbot-close");
  const input  = document.getElementById("chat-input");
  const sendB  = document.getElementById("chat-send");

  toggle.addEventListener("click", () => {
    panel.classList.toggle("hidden");
    if (!panel.classList.contains("hidden") && !state.chatHistory.length) {
      addBotMsg("¡Hola! Soy Azul 🌍, tu asistente de viajes.\n¿En qué tipo de destino estás pensando? ¿Playa, montaña o ciudad?");
    }
  });

  closeB.addEventListener("click", () => panel.classList.add("hidden"));

  sendB.addEventListener("click", sendChat);
  input.addEventListener("keydown", e => { if (e.key === "Enter") sendChat(); });
}

async function sendChat() {
  const input = document.getElementById("chat-input");
  const msg   = input.value.trim();
  if (!msg) return;
  input.value = "";

  addUserMsg(msg);
  const typing = addTypingIndicator();

  const res = await fetch("/api/chatbot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mensaje: msg }),
  }).then(r => r.json());

  typing.remove();
  addBotMsg(res.respuesta);
}

function addUserMsg(text) {
  appendMsg("user", "👤", text);
}
function addBotMsg(text) {
  appendMsg("bot", "✈️", text);
}

function appendMsg(who, icon, text) {
  const wrap = document.getElementById("chat-messages");
  const div  = document.createElement("div");
  div.className = `msg msg-${who}`;
  div.innerHTML = `
    <div class="msg-icon">${icon}</div>
    <div class="bubble">${text}</div>`;
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
  state.chatHistory.push({ who, text });
}

function addTypingIndicator() {
  const wrap = document.getElementById("chat-messages");
  const div  = document.createElement("div");
  div.className = "msg msg-bot";
  div.innerHTML = `
    <div class="msg-icon">✈️</div>
    <div class="bubble">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
  return div;
}

/* ── Utilidades ──────────────────────────────────────────────────────────── */
function stars(n) {
  const full  = Math.floor(n);
  const half  = n - full >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(empty);
}

function emoji(tipo) {
  return tipo === "playa" ? "🏖️" : tipo === "montaña" ? "🏔️" : "🏛️";
}

function cap(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function setEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function toast(msg) {
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

function showSkeletons(container, n) {
  container.innerHTML = Array(n).fill(`
    <div class="skeleton-card">
      <div class="skeleton skeleton-img"></div>
      <div class="skeleton-body">
        <div class="skeleton skeleton-line" style="width:60%"></div>
        <div class="skeleton skeleton-line" style="width:40%"></div>
        <div class="skeleton skeleton-line" style="width:50%"></div>
      </div>
    </div>`).join("");
}
