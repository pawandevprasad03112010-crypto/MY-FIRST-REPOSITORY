// Styles Injection via JS
const globalStyles = document.createElement('style');
globalStyles.textContent = `
  :root {
    --primary: #5f2eea;
    --bg-color: #f7f7fc;
    --card-bg: #ffffff;
    --text-dark: #14142b;
    --text-muted: #6e7191;
  }

  * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }
  body { display: flex; justify-content: center; background-color: var(--bg-color); }
  
  .app-frame {
    width: 100%;
    max-width: 480px;
    background: var(--card-bg);
    min-height: 100vh;
    position: relative;
    box-shadow: 0 0 15px rgba(0,0,0,0.06);
  }

  .page { display: none; padding: 16px; }
  .page.active { display: block; }

  /* Search Engine Bar Styling */
  .search-container {
    display: flex;
    align-items: center;
    position: relative;
    margin: 15px 0 20px 0;
  }

  .search-input {
    width: 100%;
    padding: 14px 50px 14px 40px;
    border-radius: 14px;
    border: 1px solid #d9dbe9;
    font-size: 0.95rem;
    outline: none;
  }

  .search-input:focus { border-color: var(--primary); }

  .search-left-icon {
    position: absolute;
    left: 14px;
    color: #a0a3bd;
    font-size: 1.1rem;
    pointer-events: none;
  }

  /* Right-side Search Button */
  .search-submit-btn {
    position: absolute;
    right: 6px;
    background: var(--primary);
    border: none;
    width: 38px;
    height: 38px;
    border-radius: 10px;
    color: #ffffff;
    font-size: 1.1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Side-scroll Image Carousel inside cards */
  .property-card {
    border-radius: 16px;
    border: 1px solid #f0f0f5;
    margin-bottom: 20px;
    overflow: hidden;
    background: var(--card-bg);
    box-shadow: 0 4px 10px rgba(0,0,0,0.02);
  }

  .horizontal-gallery {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
    gap: 8px;
    padding-bottom: 4px;
  }

  .horizontal-gallery::-webkit-scrollbar { display: none; }

  .horizontal-gallery img {
    flex: 0 0 88%;
    height: 220px;
    object-fit: cover;
    border-radius: 12px;
    scroll-snap-align: start;
  }

  .card-content { padding: 14px; cursor: pointer; }
  .badge-verified { display: inline-block; background: #e2fbd7; color: #008a00; font-size: 0.75rem; font-weight: bold; padding: 4px 8px; border-radius: 6px; margin-bottom: 8px; }
  .prop-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 6px; color: var(--text-dark); }
  .prop-price { font-size: 1.25rem; font-weight: bold; color: var(--primary); margin: 6px 0; }
  .prop-subtext { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 6px; }

  /* Detail Screen Carousel */
  .detail-gallery {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    gap: 10px;
    margin-bottom: 16px;
    scrollbar-width: none;
  }
  .detail-gallery::-webkit-scrollbar { display: none; }

  .detail-gallery img {
    flex: 0 0 100%;
    height: 300px;
    object-fit: cover;
    border-radius: 16px;
    scroll-snap-align: start;
  }
`;
document.head.appendChild(globalStyles);

// Main Container
const mainApp = document.createElement('div');
mainApp.className = 'app-frame';
document.body.appendChild(mainApp);

// 1. LOGIN PAGE
const loginPage = document.createElement('div');
loginPage.className = 'page active';
loginPage.id = 'login-page';

loginPage.innerHTML = `
  <div style="text-align: center; margin-top: 100px;">
    <h2>Welcome Back</h2>
    <p style="color: var(--text-muted); margin-bottom: 24px;">Please login to continue</p>
    <input type="text" id="login-user" value="PAWAN" placeholder="Username" style="width:100%; padding:12px; margin-bottom:12px; border:1px solid #ccc; border-radius:8px;">
    <input type="password" id="login-pass" value="123456" placeholder="Password" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #ccc; border-radius:8px;">
    <button id="login-submit" style="width:100%; padding:12px; background:var(--primary); color:white; border:none; border-radius:8px; font-size:1rem; font-weight:bold; cursor:pointer;">Login</button>
  </div>
`;
mainApp.appendChild(loginPage);

// 2. SEARCH PAGE
const homePage = document.createElement('div');
homePage.className = 'page';
homePage.id = 'home-page';

homePage.innerHTML = `
  <div style="font-weight:bold; font-size:1.2rem; margin:8px 0;">Hi <span id="username-heading">PAWAN</span>! 👋</div>

  <!-- Search Engine Bar -->
  <div class="search-container">
    <span class="search-left-icon">🔍</span>
    <input type="text" id="search-box-input" class="search-input" placeholder="Type letter, word or sentence to search...">
    <button id="search-action-btn" class="search-submit-btn">➔</button>
  </div>

  <div id="search-results-list"></div>
`;
mainApp.appendChild(homePage);

// 3. PROPERTY DETAIL PAGE
const detailPage = document.createElement('div');
detailPage.className = 'page';
detailPage.id = 'detail-page';

detailPage.innerHTML = `
  <button id="back-to-home" style="background:none; border:none; font-size:1.1rem; font-weight:bold; cursor:pointer; margin-bottom:12px;">← Back</button>
  <div class="detail-gallery" id="enlarged-gallery"></div>
  <div id="full-property-info"></div>
`;
mainApp.appendChild(detailPage);

// ROUTING & LOGIC
function navigateTo(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(pageId).classList.add('active');
}

document.getElementById('login-submit').addEventListener('click', () => {
  const username = document.getElementById('login-user').value;
  if (username) {
    document.getElementById('username-heading').innerText = username;
    navigateTo('home-page');
    executePropertySearch();
  }
});

document.getElementById('search-action-btn').addEventListener('click', executePropertySearch);
document.getElementById('search-box-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') executePropertySearch();
});
document.getElementById('back-to-home').addEventListener('click', () => navigateTo('home-page'));

// Search API Execution
async function executePropertySearch() {
  const query = document.getElementById('search-box-input').value;
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const properties = await response.json();
  displaySearchResults(properties);
}

// Render Results with Images
function displaySearchResults(properties) {
  const listContainer = document.getElementById('search-results-list');
  listContainer.innerHTML = '';

  if (!properties || properties.length === 0) {
    listContainer.innerHTML = '<p style="text-align:center; margin-top:30px; color:#a0a3bd;">No matching results found.</p>';
    return;
  }

  properties.forEach(item => {
    const card = document.createElement('div');
    card.className = 'property-card';

    const imagesHtml = (item.images || []).map(imgUrl => `<img src="${imgUrl}" alt="Property Image">`).join('');

    card.innerHTML = `
      <div class="horizontal-gallery">
        ${imagesHtml}
      </div>
      <div class="card-content" onclick="openPropertyDetail('${item._id}')">
        <span class="badge-verified">✓ Verified</span>
        <div class="prop-subtext">${item.furnishing || 'Semi-Furnished'} • ${item.size || '800 sq.ft.'}</div>
        <div class="prop-title">${item.title}</div>
        <div class="prop-price">₹ ${item.price}/Month</div>
        <div class="prop-subtext">Highlights: ${item.highlights || 'Close to Station'}</div>
      </div>
    `;
    listContainer.appendChild(card);
  });
}

// Open Detail Screen with Full Info & Enlarged Images
async function openPropertyDetail(id) {
  const res = await fetch(`/api/property/${id}`);
  const data = await res.json();

  const gallery = document.getElementById('enlarged-gallery');
  gallery.innerHTML = (data.images || []).map(imgUrl => `<img src="${imgUrl}" alt="Full Image">`).join('');

  const info = document.getElementById('full-property-info');
  info.innerHTML = `
    <span class="badge-verified">✓ Verified</span>
    <h2 style="margin: 8px 0;">${data.title}</h2>
    <div style="color: var(--text-muted); margin-bottom: 12px;">${data.location}</div>
    
    <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary); margin-bottom: 16px;">
      ₹ ${data.price} <span style="font-size:0.9rem; color:#6e7191;">/month</span>
    </div>

    <div style="background:#f8f9fa; padding:14px; border-radius:12px; margin-bottom:16px;">
      <p style="margin:6px 0;"><strong>Furnishing Status:</strong> ${data.furnishing || 'N/A'}</p>
      <p style="margin:6px 0;"><strong>Security Deposit:</strong> ₹ ${data.deposit || '3,000,00'}</p>
      <p style="margin:6px 0;"><strong>Built-up Area:</strong> ${data.size || 'N/A'}</p>
    </div>

    <h3>Description</h3>
    <p style="color: #444; line-height: 1.5;">${data.description || 'No detailed description provided.'}</p>
  `;

  navigateTo('detail-page');
                                                                 }
