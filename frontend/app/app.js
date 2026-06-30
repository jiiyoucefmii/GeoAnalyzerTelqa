const CONFIG_API_URL = window.APP_CONFIG?.apiUrl || "http://localhost:8000";
const IS_LOCAL_DEMO_PORT =
  ["localhost", "127.0.0.1"].includes(window.location.hostname) &&
  window.location.port &&
  !["3000", "8080"].includes(window.location.port);
const API_URL = IS_LOCAL_DEMO_PORT ? "" : CONFIG_API_URL;
const GOOGLE_MAPS_API_KEY = window.APP_CONFIG?.googleMapsApiKey || "";

const WILAYA_CENTERS = {
  Adrar: { lat: 27.874, lng: -0.293, zoom: 12 },
  Chlef: { lat: 36.165, lng: 1.334, zoom: 12 },
  Laghouat: { lat: 33.806, lng: 2.881, zoom: 12 },
  "Oum El Bouaghi": { lat: 35.877, lng: 7.113, zoom: 12 },
  Batna: { lat: 35.555, lng: 6.174, zoom: 12 },
  Bejaia: { lat: 36.752, lng: 5.056, zoom: 12 },
  "Béjaïa": { lat: 36.752, lng: 5.056, zoom: 12 },
  Biskra: { lat: 34.848, lng: 5.728, zoom: 12 },
  Bechar: { lat: 31.617, lng: -2.22, zoom: 12 },
  "Béchar": { lat: 31.617, lng: -2.22, zoom: 12 },
  Oran: { lat: 35.6971, lng: -0.6308, zoom: 12 },
  Alger: { lat: 36.7538, lng: 3.0588, zoom: 12 },
  Blida: { lat: 36.4722, lng: 2.8333, zoom: 12 },
  Bouira: { lat: 36.374, lng: 3.902, zoom: 12 },
  Tamanrasset: { lat: 22.785, lng: 5.522, zoom: 12 },
  Tebessa: { lat: 35.405, lng: 8.12, zoom: 12 },
  "Tébessa": { lat: 35.405, lng: 8.12, zoom: 12 },
  Tlemcen: { lat: 34.882, lng: -1.316, zoom: 12 },
  Tiaret: { lat: 35.371, lng: 1.317, zoom: 12 },
  "Tizi Ouzou": { lat: 36.7169, lng: 4.0497, zoom: 12 },
  Djelfa: { lat: 34.672, lng: 3.263, zoom: 12 },
  Jijel: { lat: 36.821, lng: 5.767, zoom: 12 },
  Constantine: { lat: 36.365, lng: 6.6147, zoom: 12 },
  Setif: { lat: 36.1911, lng: 5.4137, zoom: 12 },
  "Sétif": { lat: 36.1911, lng: 5.4137, zoom: 12 },
  Saida: { lat: 34.841, lng: 0.148, zoom: 12 },
  "Saïda": { lat: 34.841, lng: 0.148, zoom: 12 },
  Skikda: { lat: 36.879, lng: 6.907, zoom: 12 },
  "Sidi Bel Abbes": { lat: 35.193, lng: -0.641, zoom: 12 },
  "Sidi Bel Abbès": { lat: 35.193, lng: -0.641, zoom: 12 },
  Annaba: { lat: 36.9, lng: 7.766, zoom: 12 },
  Guelma: { lat: 36.462, lng: 7.428, zoom: 12 },
  Medea: { lat: 36.264, lng: 2.753, zoom: 12 },
  "Médéa": { lat: 36.264, lng: 2.753, zoom: 12 },
  Mostaganem: { lat: 35.933, lng: 0.09, zoom: 12 },
  Msila: { lat: 35.705, lng: 4.541, zoom: 12 },
  "M'Sila": { lat: 35.705, lng: 4.541, zoom: 12 },
  Mascara: { lat: 35.397, lng: 0.14, zoom: 12 },
  Ouargla: { lat: 31.953, lng: 5.325, zoom: 12 },
  "El Bayadh": { lat: 33.684, lng: 1.02, zoom: 12 },
  Illizi: { lat: 26.483, lng: 8.467, zoom: 12 },
  "Bordj Bou Arreridj": { lat: 36.073, lng: 4.761, zoom: 12 },
  Boumerdes: { lat: 36.758, lng: 3.477, zoom: 12 },
  "Boumerdès": { lat: 36.758, lng: 3.477, zoom: 12 },
  "El Tarf": { lat: 36.767, lng: 8.313, zoom: 12 },
  Tindouf: { lat: 27.671, lng: -8.148, zoom: 12 },
  Tissemsilt: { lat: 35.607, lng: 1.811, zoom: 12 },
  "El Oued": { lat: 33.371, lng: 6.867, zoom: 12 },
  Khenchela: { lat: 35.435, lng: 7.143, zoom: 12 },
  "Souk Ahras": { lat: 36.286, lng: 7.951, zoom: 12 },
  Tipaza: { lat: 36.59, lng: 2.449, zoom: 12 },
  Mila: { lat: 36.451, lng: 6.264, zoom: 12 },
  "Ain Defla": { lat: 36.264, lng: 1.968, zoom: 12 },
  "Aïn Defla": { lat: 36.264, lng: 1.968, zoom: 12 },
  Naama: { lat: 33.267, lng: -0.313, zoom: 12 },
  "Naâma": { lat: 33.267, lng: -0.313, zoom: 12 },
  "Ain Temouchent": { lat: 35.3, lng: -1.14, zoom: 12 },
  "Aïn Témouchent": { lat: 35.3, lng: -1.14, zoom: 12 },
  Ghardaia: { lat: 32.49, lng: 3.673, zoom: 12 },
  "Ghardaïa": { lat: 32.49, lng: 3.673, zoom: 12 },
  Relizane: { lat: 35.738, lng: 0.556, zoom: 12 },
  Timimoun: { lat: 29.263, lng: 0.231, zoom: 12 },
  "Bordj Badji Mokhtar": { lat: 21.327, lng: 0.946, zoom: 12 },
  "Ouled Djellal": { lat: 34.426, lng: 5.065, zoom: 12 },
  "Beni Abbes": { lat: 30.133, lng: -2.167, zoom: 12 },
  "Béni Abbès": { lat: 30.133, lng: -2.167, zoom: 12 },
  "In Salah": { lat: 27.193, lng: 2.461, zoom: 12 },
  "In Guezzam": { lat: 19.568, lng: 5.772, zoom: 12 },
  Touggourt: { lat: 33.105, lng: 6.057, zoom: 12 },
  Djanet: { lat: 24.555, lng: 9.485, zoom: 12 },
  "El Meghaier": { lat: 33.954, lng: 5.922, zoom: 12 },
  "El Meniaa": { lat: 30.583, lng: 2.883, zoom: 12 },
};

const WILAYA_ALIASES = {
  algeries: "Alger",
  algiers: "Alger",
  alger: "Alger",
  algeria: "Alger",
  setif: "Setif",
  "sétif": "Setif",
  oran: "Oran",
};

const state = {
  places: [],
  clusters: [],
  distances: [],
  selectedId: null,
  googleMap: null,
  googleReady: false,
  googleLoadStarted: false,
  infoWindow: null,
  markers: [],
  polylines: [],
  fallbackSvg: null,
};

const els = {
  wilayaInput: document.getElementById("wilayaInput"),
  categoryFilter: document.getElementById("categoryFilter"),
  statusFilter: document.getElementById("statusFilter"),
  searchInput: document.getElementById("searchInput"),
  kpis: document.getElementById("kpis"),
  map: document.getElementById("map"),
  mapNotice: document.getElementById("mapNotice"),
  placesTable: document.getElementById("placesTable"),
  distancesTable: document.getElementById("distancesTable"),
  countBadge: document.getElementById("countBadge"),
  jobStatus: document.getElementById("jobStatus"),
  automationLog: document.getElementById("automationLog"),
  csvFile: document.getElementById("csvFile"),
  form: document.getElementById("placeForm"),
  checkForm: document.getElementById("checkForm"),
};

const form = {
  placeId: document.getElementById("placeId"),
  name: document.getElementById("name"),
  category: document.getElementById("category"),
  subtype: document.getElementById("subtype"),
  phone: document.getElementById("phone"),
  website: document.getElementById("website"),
  address: document.getElementById("address"),
  lat: document.getElementById("lat"),
  lng: document.getElementById("lng"),
  wilaya: document.getElementById("wilaya"),
  commune: document.getElementById("commune"),
  sourceStatus: document.getElementById("sourceStatus"),
  score: document.getElementById("score"),
  googlePlaceId: document.getElementById("googlePlaceId"),
  googleMapsUrl: document.getElementById("googleMapsUrl"),
};

bindEvents();
loadGoogleMaps();
loadAll();

function bindEvents() {
  document.getElementById("loadBtn").addEventListener("click", loadAll);
  document.getElementById("refreshBtn").addEventListener("click", loadAll);
  document.getElementById("newStoreBtn").addEventListener("click", () => blankPlace("clothing_store"));
  document.getElementById("newDeliveryBtn").addEventListener("click", () => blankPlace("delivery_company"));
  document.getElementById("approveBtn").addEventListener("click", () => setStatus("verified"));
  document.getElementById("rejectBtn").addEventListener("click", () => setStatus("rejected"));
  document.getElementById("removeBtn").addEventListener("click", removeSelected);
  document.getElementById("googleIngestBtn").addEventListener("click", ingestGoogle);
  document.getElementById("verifyBtn").addEventListener("click", runVerification);
  document.getElementById("clustersBtn").addEventListener("click", recalcClusters);
  document.getElementById("distancesBtn").addEventListener("click", recalcDistances);
  document.getElementById("nightlyBtn").addEventListener("click", runPipeline);
  document.getElementById("exportCsvBtn").addEventListener("click", () => download(`/exports/places.csv?wilaya=${encodeURIComponent(wilaya())}`));
  document.getElementById("exportGeoJsonBtn").addEventListener("click", () => download(`/exports/places.geojson?wilaya=${encodeURIComponent(wilaya())}`));
  els.form.addEventListener("submit", savePlace);
  els.checkForm.addEventListener("submit", addCheck);
  els.csvFile.addEventListener("change", importCsv);
}

async function loadAll() {
  setStatusText("Loading data...");
  const params = new URLSearchParams();
  if (wilaya()) params.set("wilaya", wilaya());
  if (els.categoryFilter.value) params.set("category", els.categoryFilter.value);
  if (els.statusFilter.value) params.set("source_status", els.statusFilter.value);
  if (els.searchInput.value.trim()) params.set("q", els.searchInput.value.trim());
  state.places = (await api(`/places?${params}`)).filter(isTargetPlace);
  state.clusters = await api(`/clusters?wilaya=${encodeURIComponent(wilaya())}`);
  state.distances = await api(`/cluster-distances?wilaya=${encodeURIComponent(wilaya())}`);
  if (!state.selectedId || !state.places.some((p) => p.id === state.selectedId)) {
    state.selectedId = state.places[0]?.id || null;
  }
  render();
  setStatusText("Ready.");
}

function render() {
  renderKpis();
  renderMap();
  renderPlaces();
  renderDistances();
  renderForm();
}

function renderKpis() {
  const stores = state.places.filter((p) => p.category === "clothing_store");
  const deliveries = state.places.filter((p) => p.category === "delivery_company");
  const verified = state.places.filter((p) => ["verified", "manually_added"].includes(p.source_status));
  const candidates = state.places.filter((p) => p.source_status === "candidate");
  const nearestValues = nearestDistanceRows().map((row) => row.driving_distance_m).filter(Number.isFinite);
  const avgNearest = nearestValues.length ? nearestValues.reduce((a, b) => a + b, 0) / nearestValues.length : 0;
  const items = [
    ["Visible places", state.places.length],
    ["Stores", stores.length],
    ["Delivery", deliveries.length],
    ["Verified", verified.length],
    ["Candidates", candidates.length],
    ["Avg nearest", avgNearest ? formatDistance(avgNearest) : "n/a"],
  ];
  els.kpis.innerHTML = items.map(([label, value]) => `<div class="kpi"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join("");
}

function renderMap() {
  if (state.googleReady && window.google?.maps) {
    renderGoogleMap();
    return;
  }
  renderFallbackMap();
}

function loadGoogleMaps() {
  if (!GOOGLE_MAPS_API_KEY) {
    els.mapNotice.textContent = "Google Maps browser key is not configured. Showing local fallback map.";
    return;
  }
  if (state.googleLoadStarted) return;
  state.googleLoadStarted = true;
  window.initCoverageMap = () => {
    state.googleReady = true;
    els.mapNotice.textContent = "";
    renderMap();
  };
  const script = document.createElement("script");
  script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(GOOGLE_MAPS_API_KEY)}&callback=initCoverageMap&loading=async`;
  script.async = true;
  script.defer = true;
  script.onerror = () => {
    els.mapNotice.textContent = "Google Maps could not load. Check the browser API key and domain restrictions.";
    state.googleReady = false;
    renderFallbackMap();
  };
  document.head.appendChild(script);
}

function renderGoogleMap() {
  const center = centerForWilaya(wilaya());
  if (!state.googleMap) {
    state.googleMap = new google.maps.Map(els.map, {
      center,
      zoom: center.zoom,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: true,
      clickableIcons: false,
      styles: [
        { featureType: "poi", stylers: [{ visibility: "off" }] },
        { featureType: "transit", stylers: [{ visibility: "off" }] },
      ],
    });
    state.infoWindow = new google.maps.InfoWindow();
  }

  state.markers.forEach((marker) => marker.setMap(null));
  state.polylines.forEach((line) => line.setMap(null));
  state.markers = [];
  state.polylines = [];

  const bounds = new google.maps.LatLngBounds();
  let hasBounds = false;

  nearestDistanceRows().forEach((row) => {
    const cluster = state.clusters.find((c) => c.id === row.cluster_id);
    const delivery = state.places.find((p) => p.id === row.delivery_company_id);
    if (!cluster || !delivery) return;
    const gap = row.driving_distance_m > 5000;
    const line = new google.maps.Polyline({
      map: state.googleMap,
      path: [
        { lat: Number(cluster.centroid_lat), lng: Number(cluster.centroid_lng) },
        { lat: Number(delivery.lat), lng: Number(delivery.lng) },
      ],
      geodesic: true,
      strokeColor: gap ? "#ef4444" : "#2457c5",
      strokeOpacity: 0.55,
      strokeWeight: gap ? 4 : 3,
    });
    state.polylines.push(line);
  });

  state.clusters.forEach((cluster) => {
    const position = { lat: Number(cluster.centroid_lat), lng: Number(cluster.centroid_lng) };
    const marker = new google.maps.Marker({
      map: state.googleMap,
      position,
      label: { text: String(cluster.store_count), color: "#fff", fontWeight: "700" },
      icon: circleIcon("#9a3fb7", Math.max(18, Math.min(34, 14 + Number(cluster.store_count || 0) * 2))),
      title: `Cluster: ${cluster.store_count} stores`,
      zIndex: 50,
    });
    marker.addListener("click", () => {
      state.infoWindow.setContent(`<strong>Store cluster</strong><br>${cluster.store_count} stores<br>Radius ${formatDistance(cluster.radius_m)}`);
      state.infoWindow.open({ map: state.googleMap, anchor: marker });
    });
    state.markers.push(marker);
    bounds.extend(position);
    hasBounds = true;
  });

  state.places.filter(isTargetPlace).forEach((p) => {
    if (p.source_status === "rejected") return;
    const position = { lat: Number(p.lat), lng: Number(p.lng) };
    const selected = p.id === state.selectedId;
    const color = p.category === "delivery_company" ? "#2457c5" : p.source_status === "candidate" ? "#c57b13" : "#1c7c54";
    const marker = new google.maps.Marker({
      map: state.googleMap,
      position,
      icon: p.category === "delivery_company" ? triangleIcon(color, selected) : circleIcon(color, selected ? 13 : 9),
      title: p.name,
      zIndex: selected ? 100 : p.category === "delivery_company" ? 40 : 30,
    });
    marker.addListener("click", () => {
      selectPlace(p.id);
      state.infoWindow.setContent(placeInfoHtml(p));
      state.infoWindow.open({ map: state.googleMap, anchor: marker });
    });
    state.markers.push(marker);
    bounds.extend(position);
    hasBounds = true;
  });

  if (hasBounds) {
    state.googleMap.fitBounds(bounds, 54);
    google.maps.event.addListenerOnce(state.googleMap, "idle", () => {
      if (state.googleMap.getZoom() > 15) state.googleMap.setZoom(15);
    });
  } else {
    state.googleMap.setCenter(center);
    state.googleMap.setZoom(center.zoom);
  }
}

function renderFallbackMap() {
  if (state.fallbackSvg) state.fallbackSvg.remove();
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 1000 620");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Fallback coverage map");
  state.fallbackSvg = svg;
  els.map.replaceChildren(svg);

  const bounds = boundsFromPlaces(state.places);
  const project = projector(bounds);
  const parts = [
    `<rect x="0" y="0" width="1000" height="620" fill="#e8edf1"></rect>`,
    `<path d="${boundaryPath(bounds, project)}" fill="#f9fbfd" stroke="#b6c2cf" stroke-width="2"></path>`,
    gridLines(),
  ];

  nearestDistanceRows().forEach((row) => {
    const cluster = state.clusters.find((c) => c.id === row.cluster_id);
    const delivery = state.places.find((p) => p.id === row.delivery_company_id);
    if (!cluster || !delivery) return;
    const [x1, y1] = project(cluster.centroid_lat, cluster.centroid_lng);
    const [x2, y2] = project(delivery.lat, delivery.lng);
    const gap = row.driving_distance_m > 5000;
    parts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${gap ? "#ef4444" : "#2457c5"}" stroke-width="${gap ? 3 : 2}" opacity=".42" stroke-dasharray="${gap ? "7 7" : "0"}"></line>`);
  });

  state.clusters.forEach((cluster) => {
    const [x, y] = project(cluster.centroid_lat, cluster.centroid_lng);
    const r = Math.max(16, Math.min(34, 12 + cluster.store_count * 2));
    parts.push(`<g><circle cx="${x}" cy="${y}" r="${r}" fill="#9a3fb7" opacity=".86"></circle><text x="${x}" y="${y + 4}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">${cluster.store_count}</text></g>`);
  });

  state.places.filter(isTargetPlace).forEach((p) => {
    if (p.source_status === "rejected") return;
    const [x, y] = project(p.lat, p.lng);
    const selected = p.id === state.selectedId;
    const color = p.category === "delivery_company" ? "#2457c5" : p.source_status === "candidate" ? "#c57b13" : "#1c7c54";
    if (p.category === "delivery_company") {
      parts.push(`<g data-place="${p.id}" class="marker"><path d="M ${x} ${y - 13} L ${x + 13} ${y + 11} L ${x - 13} ${y + 11} Z" fill="${color}" stroke="${selected ? "#17202a" : "#fff"}" stroke-width="${selected ? 4 : 2}"><title>${esc(p.name)}</title></path></g>`);
    } else {
      parts.push(`<g data-place="${p.id}" class="marker"><circle cx="${x}" cy="${y}" r="${selected ? 10 : 7}" fill="${color}" stroke="${selected ? "#17202a" : "#fff"}" stroke-width="${selected ? 4 : 2}"><title>${esc(p.name)}</title></circle></g>`);
    }
  });

  svg.innerHTML = parts.join("");
  svg.querySelectorAll(".marker").forEach((node) => {
    node.addEventListener("click", () => selectPlace(node.dataset.place));
  });
}

function circleIcon(color, scale) {
  return {
    path: google.maps.SymbolPath.CIRCLE,
    fillColor: color,
    fillOpacity: 0.92,
    strokeColor: "#ffffff",
    strokeWeight: 2,
    scale,
  };
}

function triangleIcon(color, selected) {
  return {
    path: "M 0 -14 L 13 11 L -13 11 Z",
    fillColor: color,
    fillOpacity: 0.94,
    strokeColor: selected ? "#17202a" : "#ffffff",
    strokeWeight: selected ? 4 : 2,
    scale: 1,
    anchor: new google.maps.Point(0, 0),
  };
}

function placeInfoHtml(p) {
  return `
    <strong>${esc(p.name)}</strong><br>
    ${p.category === "delivery_company" ? "Delivery company" : "Clothing store"} / ${esc(p.subtype || "general")}<br>
    ${esc(p.commune || p.wilaya || "")}<br>
    Status: ${esc(p.source_status)} | Score: ${Number(p.verification_score || 0)}
    ${p.google_maps_url ? `<br><a href="${esc(p.google_maps_url)}" target="_blank" rel="noopener">Google Maps listing</a>` : ""}
  `;
}

function renderPlaces() {
  els.countBadge.textContent = state.places.length;
  els.placesTable.innerHTML = state.places.map((p) => `
    <tr class="${p.id === state.selectedId ? "selected" : ""}" data-id="${p.id}">
      <td>${esc(p.name)}</td>
      <td>${p.category === "delivery_company" ? "Delivery" : "Store"}</td>
      <td><span class="pill ${p.source_status}">${esc(p.source_status)}</span></td>
    </tr>
  `).join("");
  els.placesTable.querySelectorAll("tr[data-id]").forEach((row) => {
    row.addEventListener("click", () => selectPlace(row.dataset.id));
  });
}

function renderDistances() {
  const rows = nearestDistanceRows();
  els.distancesTable.innerHTML = rows.length ? rows.map((row) => `
    <tr>
      <td>${shortId(row.cluster_id)}</td>
      <td>${row.store_count}</td>
      <td>${esc(row.delivery_company_name || "n/a")}</td>
      <td>${formatDistance(row.driving_distance_m)}</td>
      <td>${formatDuration(row.driving_duration_s)}</td>
      <td>${esc(row.route_provider)}</td>
    </tr>
  `).join("") : `<tr><td colspan="6">No cluster distances yet. Recalculate clusters and distances.</td></tr>`;
}

function renderForm() {
  const p = selectedPlace();
  if (!p) {
    blankPlace("clothing_store", false);
    return;
  }
  form.placeId.value = p.id;
  form.name.value = p.name || "";
  form.category.value = p.category || "clothing_store";
  form.subtype.value = p.subtype || "";
  form.phone.value = p.phone || "";
  form.website.value = p.website || "";
  form.address.value = p.address_text || "";
  form.lat.value = p.lat ?? "";
  form.lng.value = p.lng ?? "";
  form.wilaya.value = p.wilaya || wilaya();
  form.commune.value = p.commune || "";
  form.sourceStatus.value = p.source_status || "candidate";
  form.score.value = p.verification_score || 0;
  form.googlePlaceId.value = p.google_place_id || "";
  form.googleMapsUrl.value = p.google_maps_url || "";
}

async function savePlace(event) {
  event.preventDefault();
  const payload = formPayload();
  if (form.placeId.value) {
    await api(`/places/${form.placeId.value}`, { method: "PATCH", body: payload });
  } else {
    const created = await api("/places", { method: "POST", body: payload });
    state.selectedId = created.id;
  }
  await loadAll();
}

async function setStatus(sourceStatus) {
  if (!state.selectedId) return;
  await api(`/places/${state.selectedId}`, { method: "PATCH", body: { source_status: sourceStatus, verification_score: sourceStatus === "verified" ? Math.max(Number(form.score.value), 75) : Number(form.score.value) } });
  await loadAll();
}

async function removeSelected() {
  if (!state.selectedId || !confirm("Deactivate this place?")) return;
  await api(`/places/${state.selectedId}`, { method: "DELETE" });
  state.selectedId = null;
  await loadAll();
}

async function addCheck(event) {
  event.preventDefault();
  if (!state.selectedId) return;
  await api(`/places/${state.selectedId}/verification-checks`, {
    method: "POST",
    body: {
      check_type: document.getElementById("checkType").value,
      result: document.getElementById("checkResult").value,
      details: document.getElementById("checkDetails").value,
      checked_by: "dashboard",
    },
  });
  document.getElementById("checkDetails").value = "";
  await loadAll();
}

async function ingestGoogle() {
  const queries = [
    `clothing store in ${wilaya()} Algeria`,
    `boutique vetement in ${wilaya()} Algeria`,
    `magasin vetements in ${wilaya()} Algeria`,
    `women clothing store in ${wilaya()} Algeria`,
    `men clothing store in ${wilaya()} Algeria`,
    `kids clothing store in ${wilaya()} Algeria`,
    `shoe store in ${wilaya()} Algeria`,
    `sportswear store in ${wilaya()} Algeria`,
    `delivery company in ${wilaya()} Algeria`,
    `courier service in ${wilaya()} Algeria`,
    `shipping service in ${wilaya()} Algeria`,
    `societe de livraison in ${wilaya()} Algeria`,
  ];
  setStatusText("Running Google Places candidate discovery...");
  const result = await api("/ingestion/google-places", { method: "POST", body: { wilaya: wilaya(), queries, included_types: [], max_pages_per_query: 3, enqueue: false } });
  reportJob("Google Candidates", result);
  await loadAll();
}

async function runVerification() {
  setStatusText("Running verification checks...");
  const result = await api("/verification/run", { method: "POST", body: { wilaya: wilaya() } });
  reportJob("Verification", result);
  await loadAll();
}

async function recalcClusters() {
  setStatusText("Recalculating clusters...");
  const eps = Number(document.getElementById("clusterEps").value || 1000);
  const minSamples = Number(document.getElementById("clusterMin").value || 2);
  const result = await api("/analysis/clusters/recalculate", { method: "POST", body: { wilaya: wilaya(), eps_m: eps, min_samples: minSamples } });
  reportJob("Clusters", result);
  await loadAll();
}

async function recalcDistances() {
  setStatusText("Recalculating distances...");
  const result = await api("/analysis/distances/recalculate", { method: "POST", body: { wilaya: wilaya(), use_google_routes: true } });
  reportJob("Distances", result);
  await loadAll();
}

async function runPipeline() {
  await ingestGoogle();
  await runVerification();
  await recalcClusters();
  await recalcDistances();
}

async function importCsv() {
  const file = els.csvFile.files[0];
  if (!file) return;
  const data = new FormData();
  data.append("file", file);
  setStatusText("Importing CSV...");
  const response = await fetch(`${API_URL}/imports/places.csv`, { method: "POST", body: data });
  if (!response.ok) throw new Error(await response.text());
  const result = await response.json();
  reportJob("CSV Import", result);
  els.csvFile.value = "";
  await loadAll();
}

function blankPlace(category, select = true) {
  const center = centerForWilaya(wilaya());
  if (select) state.selectedId = null;
  form.placeId.value = "";
  form.name.value = category === "delivery_company" ? "New delivery company" : "New clothing store";
  form.category.value = category;
  form.subtype.value = category === "delivery_company" ? "courier" : "general";
  form.phone.value = "";
  form.website.value = "";
  form.address.value = "";
  form.lat.value = String(center.lat);
  form.lng.value = String(center.lng);
  form.wilaya.value = wilaya();
  form.commune.value = "";
  form.sourceStatus.value = "manually_added";
  form.score.value = "70";
  form.googlePlaceId.value = "";
  form.googleMapsUrl.value = "";
}

function formPayload() {
  return {
    name: form.name.value.trim(),
    category: form.category.value,
    subtype: form.subtype.value.trim() || null,
    phone: form.phone.value.trim() || null,
    website: form.website.value.trim() || null,
    address_text: form.address.value.trim() || null,
    lat: Number(form.lat.value),
    lng: Number(form.lng.value),
    wilaya: form.wilaya.value.trim(),
    commune: form.commune.value.trim() || null,
    source_status: form.sourceStatus.value,
    verification_score: Number(form.score.value || 0),
    google_place_id: form.googlePlaceId.value.trim() || null,
    google_maps_url: form.googleMapsUrl.value.trim() || null,
  };
}

async function api(path, options = {}) {
  const init = { ...options };
  if (init.body && !(init.body instanceof FormData)) {
    init.headers = { "Content-Type": "application/json", ...(init.headers || {}) };
    init.body = JSON.stringify(init.body);
  }
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    setStatusText(text);
    throw new Error(text);
  }
  return response.json();
}

function download(path) {
  window.location.href = `${API_URL}${path}`;
}

function selectPlace(id) {
  state.selectedId = id;
  render();
}

function selectedPlace() {
  return state.places.find((p) => p.id === state.selectedId);
}

function wilaya() {
  const raw = els.wilayaInput.value.trim() || "Oran";
  const canonical = resolveWilayaName(raw);
  if (canonical !== raw) {
    els.wilayaInput.value = canonical;
  }
  return canonical;
}

function centerForWilaya(name) {
  const canonical = resolveWilayaName(name);
  return WILAYA_CENTERS[canonical] || WILAYA_CENTERS[normalizeWilayaName(canonical)] || { lat: 28.0339, lng: 1.6596, zoom: 6 };
}

function normalizeWilayaName(name) {
  return String(name || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/'/g, "")
    .toLowerCase()
    .trim();
}

function resolveWilayaName(name) {
  const normalized = normalizeWilayaName(name);
  if (WILAYA_ALIASES[normalized]) return WILAYA_ALIASES[normalized];
  const match = Object.keys(WILAYA_CENTERS).find((wilayaName) => normalizeWilayaName(wilayaName) === normalized);
  return match || String(name || "Oran").trim() || "Oran";
}

function isTargetPlace(place) {
  return ["clothing_store", "delivery_company"].includes(place?.category);
}

function setStatusText(text) {
  els.jobStatus.textContent = text;
}

function reportJob(label, result) {
  const data = result.data || {};
  const text = `${result.message}: ${Object.entries(data).map(([key, value]) => `${key}=${value}`).join(", ") || "done"}`;
  setStatusText(text);
  const item = document.createElement("div");
  item.innerHTML = `<strong>${new Date().toLocaleTimeString()}</strong> ${esc(label)} - ${esc(text)}`;
  els.automationLog.prepend(item);
}

function nearestDistanceRows() {
  const byCluster = new Map();
  state.distances.forEach((row) => {
    const current = byCluster.get(row.cluster_id);
    if (!current || row.driving_distance_m < current.driving_distance_m) byCluster.set(row.cluster_id, row);
  });
  return Array.from(byCluster.values());
}

function boundsFromPlaces(places) {
  if (!places.length) return { minLat: 35.58, maxLat: 35.83, minLng: -0.82, maxLng: -0.48 };
  const lats = places.map((p) => p.lat);
  const lngs = places.map((p) => p.lng);
  const padLat = Math.max((Math.max(...lats) - Math.min(...lats)) * .25, .03);
  const padLng = Math.max((Math.max(...lngs) - Math.min(...lngs)) * .25, .03);
  return {
    minLat: Math.min(...lats) - padLat,
    maxLat: Math.max(...lats) + padLat,
    minLng: Math.min(...lngs) - padLng,
    maxLng: Math.max(...lngs) + padLng,
  };
}

function projector(bounds) {
  const pad = 56;
  const width = 1000 - pad * 2;
  const height = 620 - pad * 2;
  return (lat, lng) => [
    Math.round(pad + ((lng - bounds.minLng) / Math.max(bounds.maxLng - bounds.minLng, 0.0001)) * width),
    Math.round(pad + ((bounds.maxLat - lat) / Math.max(bounds.maxLat - bounds.minLat, 0.0001)) * height),
  ];
}

function boundaryPath(bounds, project) {
  const points = [
    [bounds.maxLat, bounds.minLng],
    [bounds.maxLat - (bounds.maxLat - bounds.minLat) * .08, bounds.maxLng],
    [bounds.minLat + (bounds.maxLat - bounds.minLat) * .12, bounds.maxLng - (bounds.maxLng - bounds.minLng) * .04],
    [bounds.minLat, bounds.minLng + (bounds.maxLng - bounds.minLng) * .12],
  ].map(([lat, lng]) => project(lat, lng));
  return `M ${points[0][0]} ${points[0][1]} L ${points[1][0]} ${points[1][1]} L ${points[2][0]} ${points[2][1]} L ${points[3][0]} ${points[3][1]} Z`;
}

function gridLines() {
  const lines = [];
  for (let x = 140; x < 920; x += 120) lines.push(`<line x1="${x}" y1="54" x2="${x}" y2="566" stroke="#c8d2dc" stroke-width="1" opacity=".55"></line>`);
  for (let y = 110; y < 550; y += 90) lines.push(`<line x1="54" y1="${y}" x2="946" y2="${y}" stroke="#c8d2dc" stroke-width="1" opacity=".55"></line>`);
  return lines.join("");
}

function formatDistance(meters) {
  if (!Number.isFinite(Number(meters))) return "n/a";
  return meters >= 1000 ? `${(meters / 1000).toFixed(1)} km` : `${Math.round(meters)} m`;
}

function formatDuration(seconds) {
  if (!Number.isFinite(Number(seconds))) return "n/a";
  return `${Math.max(1, Math.round(seconds / 60))} min`;
}

function shortId(id) {
  return String(id).slice(0, 8);
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
