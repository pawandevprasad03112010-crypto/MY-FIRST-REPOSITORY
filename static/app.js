// Global Styles Injection via JS
const style = document.createElement('style');
style.textContent = `
  :root { --primary: #5f2eea; --bg: #f7f7fc; }
  * { box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
  .app-card { width: 100%; max-width: 480px; margin: 0 auto; min-height: 100vh; background: #fff; position: relative; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
  .screen { display: none; padding: 16px; }
  .screen.active { display: block; }
  .carousel { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; gap: 8px; }
  .carousel::-webkit-scrollbar { display: none; }
  .carousel img { flex: 0 0 85%; height: 200px; object-fit: cover; border-radius: 12px; scroll-snap-align: start; }
  .detail-carousel img { flex: 0 0 100%; height: 280px; object-fit: cover; border-radius: 16px; scroll-snap-align: start; }
  .prop-card { border: 1px solid #f0f0f5; border-radius: 16px; margin-bottom: 16px; overflow: hidden; background: #fff; cursor: pointer; }
  .badge { display: inline-block; background: #e2fbd7; color: #008a00; font-size: 0.75rem; font-weight: bold; padding: 4px 8px; border-radius: 6px; }
`;
document.head.appendChild(style);

// Main Container
const appContainer = document.createElement('div');
appContainer.className = 'app-card';
document.body.appendChild(appContainer);

// ------------------- 1. LOGIN SCREEN -------------------
const loginScreen = document.createElement('div');
loginScreen.className = 'screen active';
loginScreen.id = 'login-screen';

loginScreen.innerHTML = `
  <div style="text-align: center; padding-top: 100px;">
    <h2>Welcome Back</h2>
    <p style="color:#6e7191;">Sign in to view properties</p>
    <input type="text" id="username" value="PAWAN" placeholder="Username" style="width:100%; padding:12px; margin:10px 0; border:1px solid #ccc; border-radius:8px;">
    <input type="password" id="password" value="123456" placeholder="Password" style="width:100%; padding:12px; margin:10px 0; border:1px solid #ccc; border-radius:8px;">
    <button id="login-btn" style="width:100%; padding:12px; background:var(--primary); color:#fff; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">Login</button>
  </div>
`;
appContainer.appendChild(loginScreen);

// ------------------- 2. HOME SCREEN -------------------
const homeScreen = document.createElement('div');
homeScreen.className = 'screen';
homeScreen.id = 'home-screen';

homeScreen.innerHTML = `
  <div style="font-weight:bold; font-size:1.2rem; margin-bottom:12px;">Hi <span id="user-display">PAWAN</span>! 👋</div>
  
  <div style="display:flex; gap:10px; overflow-x:auto; margin-bottom:15px; padding-bottom:5px;">
    <div style="padding:8px 14px; background:#f0efff; color:var(--primary); border-radius:10px; font-weight:bold; white-space:nowrap;">Projects</div>
    <div style="padding:8px 14px; background:#f0efff; color:var(--primary); border-radius:10px; font-weight:bold; white-space:nowrap;">Buy</div>
    <div style="padding:8px 14px; background:#f0efff; color:var(--primary); border-radius:10px; font-weight:bold; white-space:nowrap;">Rent</div>
  </div>

  <div style="position:relative; margin-bottom:20px;">
    <input type="text" id="search-input" placeholder="Search locality or project..." style="width:100%; padding:12px 40px 12px 12px; border-radius:12px; border:1px solid #d9dbe9; outline:none;">
    <button id="search-btn" style="position:absolute; right:6px; top:6px; background:var(--primary); color:white; border:none; width:32px; height:32px; border-radius:8px; cursor:pointer;">🔍</button>
  </div>

  <div id="property-list"></div>
`;
appContainer.appendChild(homeScreen);

// ------------------- 3. DETAIL SCREEN -------------------
const detailScreen = document.createElement('div');
detailScreen.className = 'screen';
detailScreen.id = 'detail-screen';

detailScreen.innerHTML = `
  <button id="back-btn" style="background:none; border:none; font-size:1rem; font-weight:bold; cursor:pointer; margin-bottom:12px;">← Back</button>
  <div class="carousel detail-carousel" id="detail-gallery"></div>
  <div id="detail-info" style="margin-top:15px;"></div>
`;
appContainer.appendChild(detailScreen);

// ------------------- LOGIC & ROUTING -------------------

function switchScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(screenId).classList.add('active');
}

// Event Listeners
document.getElementById('login-btn').addEventListener('click', () => {
  const user = document.getElementById('username').value;
  if (user) {
    document.getElementById('user-display').innerText = user;
    switchScreen('home-screen');
    fetchProperties();
  }
});

document.getElementById('search-btn').addEventListener('click', fetchProperties);
document.getElementById('search-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') fetchProperties();
});

document.getElementById('back-btn').addEventListener('click', () => {
  switchScreen('home-screen');
});

// Search API Handler
async function fetchProperties() {
  const query = document.getElementById('search-input').value;
  const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const data = await res.json();
  renderProperties(data);
}

// Render Results
function renderProperties(list) {
  const container = document.getElementById('property-list');
  container.innerHTML = '';

  if (list.length === 0) {
    container.innerHTML = '<p style="text-align:center; color:#888;">No properties found.</p>';
    return;
  }

  list.forEach(item => {
    const card = document.createElement('div');
    card.className = 'prop-card';

    const imagesHtml = (item.images || []).map(url => `<img src="${url}">`).join('');

    card.innerHTML = `
      <div class="carousel">${imagesHtml}</div>
      <div style="padding:12px;" onclick="loadDetail('${item._id}')">
        <span class="badge">✓ Verified</span>
        <div style="font-size:0.85rem; color:#6e7191; margin:4px 0;">${item.furnishing || 'Semi-Furnished'} • ${item.size || '800 sq.ft.'}</div>
        <div style="font-weight:bold; font-size:1rem;">${item.title}</div>
        <div style="font-size:1.1rem; font-weight:bold; color:var(--primary); margin:6px 0;">₹ ${item.price}/Month</div>
        <div style="font-size:0.8rem; color:#6e7191;">Highlights: ${item.highlights || 'N/A'}</div>
      </div>
    `;
    container.appendChild(card);
  });
}

// Detail Page Handler
async function loadDetail(id) {
  const res = await fetch(`/api/property/${id}`);
  const data = await res.json();

  const gallery = document.getElementById('detail-gallery');
  gallery.innerHTML = (data.images || []).map(url => `<img src="${url}">`).join('');

  const info = document.getElementById('detail-info');
  info.innerHTML = `
    <span class="badge">✓ Verified</span>
    <h2 style="margin:8px 0 4px 0;">${data.title}</h2>
    <div style="color:#6e7191; margin-bottom:8px;">${data.location}</div>
    <div style="font-size:1.4rem; font-weight:bold; color:var(--primary);">₹ ${data.price} <span style="font-size:0.9rem; color:#666;">/month</span></div>
    
    <div style="background:#f8f9fa; padding:12px; border-radius:10px; margin-top:15px;">
      <p style="margin:4px 0;"><strong>Furnishing:</strong> ${data.furnishing || 'N/A'}</p>
      <p style="margin:4px 0;"><strong>Deposit:</strong> ₹ ${data.deposit || '3,000,00'}</p>
      <p style="margin:4px 0;"><strong>Size:</strong> ${data.size || 'N/A'}</p>
    </div>
    <p style="color:#444; margin-top:12px; line-height:1.4;">${data.description || ''}</p>
  `;

  switchScreen('detail-screen');
}

