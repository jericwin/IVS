import os
import re

# 1. Update Navigation Links in all buyer templates
buyer_templates_dir = 'templates/buyer'
address_template = 'templates/addresses.html'
profile_template = 'templates/profile.html'

nav_cart_link = """      <a href="/buyer/cart" style="display: inline-flex; align-items: center; gap: 4px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
        Cart {% if cart_item_count and cart_item_count > 0 %}<span style="background: var(--accent); color: var(--bg-primary); padding: 2px 6px; border-radius: 10px; font-size: 0.7rem;">{{ cart_item_count }}</span>{% endif %}
      </a>"""

all_files = [os.path.join(root, f) for root, _, files in os.walk(buyer_templates_dir) for f in files if f.endswith('.html')]
if os.path.exists(address_template): all_files.append(address_template)
if os.path.exists(profile_template): all_files.append(profile_template)

for filepath in all_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<a href="/buyer/cart"' not in content:
        # insert after purchases
        pattern1 = r'(<a href="/buyer/purchases"[^>]*>My Purchases</a>)'
        pattern2 = r'(<a href="/buyer/purchases">My Purchases</a>)'
        
        if re.search(pattern1, content):
            new_content = re.sub(pattern1, r'\1\n' + nav_cart_link, content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        elif re.search(pattern2, content):
            new_content = re.sub(pattern2, r'\1\n' + nav_cart_link, content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

# 2. Rewrite checkout.html
checkout_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Checkout | IVS Marketplace</title>
  <meta name="description" content="Checkout">
  <link rel="stylesheet" href="/static/style.css">
  <link rel="icon" type="image/png" href="/static/images/logo.png">
  <style>
    .dashboard-layout { display: flex; flex-direction: column; min-height: 100vh; padding-top: 80px; }
    .nav { background: color-mix(in srgb, var(--bg-primary) 95%, transparent); border-bottom: 1px solid var(--border-subtle); }
    .nav-profile { display: flex; align-items: center; gap: 12px; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--accent); color: var(--bg-primary); display: flex; align-items: center; justify-content: center; font-weight: 700; font-family: var(--font-display); font-size: 1.2rem; }
    .main-content { flex: 1; padding: 60px 5%; max-width: 800px; margin: 0 auto; width: 100%; }
    .checkout-container { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 40px; animation: fadeUp 0.8s var(--ease-out-expo) forwards; }
  </style>
</head>
<body>

  <!-- Flash Messages -->
  <div style="position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 1000; display: flex; flex-direction: column; gap: 10px; width: 100%; max-width: 400px; pointer-events: none;">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div style="background: var(--accent); color: var(--bg-primary); padding: 16px 24px; border-radius: 8px; text-align: center; font-weight: 500; box-shadow: 0 10px 30px rgba(0,0,0,0.5); animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
  </div>

  <nav class="nav" id="navbar">
    <a href="/" class="nav-logo"><img src="/static/images/logo.png" alt="IVS Logo"></a>
    <div class="nav-links" id="navLinks">
      <a href="/buyer/marketplace">Marketplace</a>
      <a href="/buyer/purchases">My Purchases</a>
      <a href="/buyer/cart" style="display: inline-flex; align-items: center; gap: 4px; color: var(--accent);">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
        Cart {% if cart_item_count and cart_item_count > 0 %}<span style="background: var(--accent); color: var(--bg-primary); padding: 2px 6px; border-radius: 10px; font-size: 0.7rem;">{{ cart_item_count }}</span>{% endif %}
      </a>
      <a href="/buyer/settings">Settings</a>
      <div class="theme-switch-wrapper" style="margin-left: 20px;">
        <label class="theme-switch">
          <input type="checkbox" onchange="const ev = new Event('change'); this.dispatchEvent(ev);" class="theme-checkbox" />
          <div class="slider round">
            <span class="icon-sun" style="display:flex; color:var(--text-secondary);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg></span>
            <span class="icon-moon" style="display:flex; color:var(--text-secondary);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg></span>
          </div>
        </label>
      </div>
      <div style="position: relative; margin-left: 20px;">
        <div class="nav-profile" style="cursor: pointer;" onclick="const menu = this.nextElementSibling; menu.style.display = menu.style.display === 'block' ? 'none' : 'block';">
          <div class="avatar">{{ current_user.first_name[0] if current_user.first_name else 'U' }}</div>
          <span style="font-size: 0.9rem; font-weight: 500;">{{ current_user.first_name }}</span>
        </div>
        <div style="display: none; position: absolute; top: 120%; right: 0; background: var(--bg-card); border: 1px solid var(--border-subtle); padding: 16px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); min-width: 200px; z-index: 100;">
          <a href="/profile" class="auth-btn" style="display: block; width: 100%; text-align: center; margin-top: 0; margin-bottom: 8px; padding: 10px; font-size: 0.75rem; text-decoration: none; box-sizing: border-box; background: transparent; border: 1px solid var(--accent); color: var(--accent) !important;">My Profile</a>
          <a href="/logout" class="auth-btn" style="display: block; width: 100%; text-align: center; margin-top: 0; padding: 10px; font-size: 0.75rem; text-decoration: none; box-sizing: border-box; color: white !important;">Logout</a>
        </div>
      </div>
    </div>
  </nav>

  <div class="dashboard-layout">
    <main class="main-content">
      
      <a href="/buyer/cart" style="color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 4px; margin-bottom: 32px; transition: 0.3s;" onmouseover="this.style.color='var(--accent)'" onmouseout="this.style.color='var(--text-secondary)'">
        &larr; Back to Cart
      </a>

      <div class="checkout-layout" style="display: flex; flex-direction: column; gap: 16px;">
        
        <!-- Delivery Address Section -->
        <div style="background: var(--bg-card); border-top: 3px dashed var(--accent); border-radius: 4px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h2 style="font-size: 1.1rem; color: var(--accent); display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
            Delivery Address
          </h2>
          {% if default_address %}
          <div style="display: flex; align-items: flex-start; gap: 16px;">
            <div style="font-weight: 600; min-width: 150px;" id="display-name-phone">{{ default_address.recipient_name }} <br><span style="font-weight: normal; color: var(--text-secondary);">{{ default_address.phone }}</span></div>
            <div style="flex: 1; color: var(--text-primary);" id="display-street-address">{{ default_address.street_address }}</div>
            <a href="javascript:void(0)" onclick="document.getElementById('addressModal').style.display='flex';" style="color: var(--accent); text-decoration: none; font-size: 0.9rem;">Change</a>
          </div>
          {% else %}
          <div style="color: var(--text-secondary);">No delivery address found. Please <a href="/profile/addresses" style="color: var(--accent);">add an address</a> first.</div>
          {% endif %}
        </div>

        <!-- Product Ordered Section -->
        <div style="background: var(--bg-card); border-radius: 4px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h2 style="font-size: 1.1rem; margin-bottom: 16px;">Products Ordered</h2>
          
          {% for item in cart_items %}
          <div style="display: flex; align-items: center; gap: 16px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 16px; margin-bottom: 16px;">
            <img src="/static/uploads/{{ item.asset.image_filename }}" alt="{{ item.asset.name }}" onerror="this.src='/static/images/product-1.png'" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;">
            <div style="flex: 1;">
              <div style="font-weight: 600; font-size: 1.1rem;">{{ item.asset.name }}</div>
              {% if item.variation %}
              <div style="color: var(--accent); font-size: 0.9rem; font-weight: 500; margin-top: 4px;">Variation: {{ item.variation }}</div>
              {% endif %}
              <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 4px;">Category: {{ item.asset.category }}</div>
            </div>
            <div style="text-align: right;">
              <div style="color: var(--text-secondary);">Unit Price (x{{ item.quantity }})</div>
              <div style="font-weight: 600;">₱{{ "{:,.2f}".format(item.asset.price) }}</div>
            </div>
          </div>
          {% endfor %}
          
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 500;">Order Total ({{ cart_items|length }} Items):</span>
            <span style="font-size: 1.2rem; font-weight: 600; color: var(--accent-light);">₱{{ "{:,.2f}".format(total_price) }}</span>
          </div>
        </div>

        <form method="POST" action="/buyer/checkout" style="display: flex; flex-direction: column; gap: 16px;">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
          <input type="hidden" name="address_id" id="address_id_input" value="{{ default_address.id if default_address else '' }}">
          
          <!-- Payment Method Section -->
          <div style="background: var(--bg-card); border-radius: 4px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h2 style="font-size: 1.1rem; margin-bottom: 16px;">Payment Method</h2>
            <div style="display: flex; gap: 16px; margin-bottom: 24px;">
              <label style="border: 1px solid var(--accent); padding: 10px 20px; border-radius: 4px; cursor: pointer; color: var(--accent); position: relative;">
                <input type="radio" name="payment_method" value="cod" checked style="display: none;">
                Cash on Delivery
                <div class="active-indicator" style="position: absolute; bottom: -1px; right: -1px; width: 0; height: 0; border-bottom: 16px solid var(--accent); border-left: 16px solid transparent;"></div>
              </label>
              <label style="border: 1px solid var(--border-subtle); padding: 10px 20px; border-radius: 4px; cursor: pointer; color: var(--text-secondary);">
                <input type="radio" name="payment_method" value="ewallet" style="display: none;">
                E-Wallet
              </label>
            </div>
            
            <div style="border-top: 1px solid var(--border-subtle); padding-top: 24px;">
              <div style="display: flex; justify-content: flex-end; gap: 40px; margin-bottom: 12px; font-size: 0.95rem;">
                <span style="color: var(--text-secondary);">Merchandise Subtotal:</span>
                <span style="min-width: 100px; text-align: right;">₱{{ "{:,.2f}".format(total_price) }}</span>
              </div>
              <div style="display: flex; justify-content: flex-end; gap: 40px; margin-bottom: 12px; font-size: 0.95rem;">
                <span style="color: var(--text-secondary);">Shipping Total:</span>
                <span style="min-width: 100px; text-align: right;">₱0.00</span>
              </div>
              <div style="display: flex; justify-content: flex-end; gap: 40px; margin-bottom: 24px; font-size: 1.1rem; font-weight: 600;">
                <span>Total Payment:</span>
                <span style="min-width: 100px; text-align: right; color: var(--accent-light);">₱{{ "{:,.2f}".format(total_price) }}</span>
              </div>
              
              <div style="display: flex; justify-content: flex-end;">
                <button type="submit" class="auth-btn" style="width: auto; padding: 16px 48px; margin: 0; font-size: 1.1rem;" {% if not default_address %}disabled style="opacity:0.5;cursor:not-allowed;"{% endif %}>Place Order</button>
              </div>
            </div>
          </div>
        </form>

      </div>

    </main>
  </div>

  <!-- Address Selection Modal -->
  <div id="addressModal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div style="background: var(--bg-card); padding: 32px; border-radius: 8px; width: 100%; max-width: 600px; border: 1px solid var(--border-subtle); max-height: 80vh; overflow-y: auto;">
      <h2 style="font-size: 1.2rem; margin-bottom: 24px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 12px;">My Addresses</h2>
      
      <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px;">
        {% for addr in addresses %}
        <label style="display: flex; align-items: flex-start; gap: 16px; cursor: pointer; padding: 16px; border: 1px solid {% if default_address and addr.id == default_address.id %}var(--accent){% else %}var(--border-subtle){% endif %}; border-radius: 4px; transition: 0.3s;" onclick="selectAddress(this, '{{ addr.id }}', '{{ addr.recipient_name }}', '{{ addr.phone }}', '{{ addr.street_address }}')">
          <input type="radio" name="modal_address" value="{{ addr.id }}" {% if default_address and addr.id == default_address.id %}checked{% endif %} style="margin-top: 4px;">
          <div>
            <div style="font-weight: 600; display: flex; align-items: center; gap: 8px;">
              {{ addr.recipient_name }} 
              <span style="font-weight: normal; color: var(--text-secondary); font-size: 0.9rem;">| {{ addr.phone }}</span>
              {% if addr.is_default %}
              <span style="font-size: 0.7rem; color: var(--accent); border: 1px solid var(--accent); padding: 2px 6px; border-radius: 4px; text-transform: uppercase;">Default</span>
              {% endif %}
            </div>
            <div style="color: var(--text-secondary); margin-top: 4px;">{{ addr.street_address }}</div>
          </div>
        </label>
        {% else %}
        <p style="color: var(--text-secondary);">No addresses found.</p>
        {% endfor %}
      </div>
      
      <div style="display: flex; justify-content: flex-end; gap: 12px;">
        <button onclick="document.getElementById('addressModal').style.display='none';" class="auth-btn" style="width: auto; padding: 10px 20px; margin: 0; background: transparent; border: 1px solid var(--border-subtle); color: var(--text-primary);">Cancel</button>
        <button onclick="confirmAddress()" class="auth-btn" style="width: auto; padding: 10px 20px; margin: 0;">Confirm</button>
      </div>
    </div>
  </div>

  <script src="/static/theme.js"></script>
  <script>
    let tempSelectedId = null;
    let tempSelectedName = null;
    let tempSelectedPhone = null;
    let tempSelectedStreet = null;

    function selectAddress(labelEl, id, name, phone, street) {
      // Highlight selected
      const labels = document.querySelectorAll('input[name="modal_address"]');
      labels.forEach(radio => {
        radio.closest('label').style.borderColor = 'var(--border-subtle)';
      });
      labelEl.style.borderColor = 'var(--accent)';
      labelEl.querySelector('input').checked = true;
      
      tempSelectedId = id;
      tempSelectedName = name;
      tempSelectedPhone = phone;
      tempSelectedStreet = street;
    }

    function confirmAddress() {
      if (tempSelectedId) {
        document.getElementById('address_id_input').value = tempSelectedId;
        document.getElementById('display-name-phone').innerHTML = `${tempSelectedName} <br><span style="font-weight: normal; color: var(--text-secondary);">${tempSelectedPhone}</span>`;
        document.getElementById('display-street-address').innerText = tempSelectedStreet;
      }
      document.getElementById('addressModal').style.display = 'none';
    }
  </script>
</body>
</html>"""

with open('templates/buyer/checkout.html', 'w', encoding='utf-8') as f:
    f.write(checkout_html)


# 3. Create cart.html
cart_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shopping Cart | IVS Marketplace</title>
  <link rel="stylesheet" href="/static/style.css">
  <link rel="icon" type="image/png" href="/static/images/logo.png">
  <style>
    .dashboard-layout { display: flex; flex-direction: column; min-height: 100vh; padding-top: 80px; }
    .nav { background: color-mix(in srgb, var(--bg-primary) 95%, transparent); border-bottom: 1px solid var(--border-subtle); }
    .nav-profile { display: flex; align-items: center; gap: 12px; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--accent); color: var(--bg-primary); display: flex; align-items: center; justify-content: center; font-weight: 700; font-family: var(--font-display); font-size: 1.2rem; }
    .main-content { flex: 1; padding: 60px 5%; max-width: 1000px; margin: 0 auto; width: 100%; }
    .cart-container { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 40px; animation: fadeUp 0.8s var(--ease-out-expo) forwards; }
  </style>
</head>
<body>

  <!-- Flash Messages -->
  <div style="position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 1000; display: flex; flex-direction: column; gap: 10px; width: 100%; max-width: 400px; pointer-events: none;">
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div style="background: var(--accent); color: var(--bg-primary); padding: 16px 24px; border-radius: 8px; text-align: center; font-weight: 500; box-shadow: 0 10px 30px rgba(0,0,0,0.5); animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
  </div>

  <nav class="nav" id="navbar">
    <a href="/" class="nav-logo"><img src="/static/images/logo.png" alt="IVS Logo"></a>
    <div class="nav-links" id="navLinks">
      <a href="/buyer/marketplace">Marketplace</a>
      <a href="/buyer/purchases">My Purchases</a>
      <a href="/buyer/cart" style="display: inline-flex; align-items: center; gap: 4px; color: var(--accent);">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
        Cart {% if cart_item_count and cart_item_count > 0 %}<span style="background: var(--accent); color: var(--bg-primary); padding: 2px 6px; border-radius: 10px; font-size: 0.7rem;">{{ cart_item_count }}</span>{% endif %}
      </a>
      <a href="/buyer/settings">Settings</a>
      <div class="theme-switch-wrapper" style="margin-left: 20px;">
        <label class="theme-switch">
          <input type="checkbox" onchange="const ev = new Event('change'); this.dispatchEvent(ev);" class="theme-checkbox" />
          <div class="slider round">
            <span class="icon-sun" style="display:flex; color:var(--text-secondary);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg></span>
            <span class="icon-moon" style="display:flex; color:var(--text-secondary);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg></span>
          </div>
        </label>
      </div>
      <div style="position: relative; margin-left: 20px;">
        <div class="nav-profile" style="cursor: pointer;" onclick="const menu = this.nextElementSibling; menu.style.display = menu.style.display === 'block' ? 'none' : 'block';">
          <div class="avatar">{{ current_user.first_name[0] if current_user.first_name else 'U' }}</div>
          <span style="font-size: 0.9rem; font-weight: 500;">{{ current_user.first_name }}</span>
        </div>
        <div style="display: none; position: absolute; top: 120%; right: 0; background: var(--bg-card); border: 1px solid var(--border-subtle); padding: 16px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); min-width: 200px; z-index: 100;">
          <a href="/profile" class="auth-btn" style="display: block; width: 100%; text-align: center; margin-top: 0; margin-bottom: 8px; padding: 10px; font-size: 0.75rem; text-decoration: none; box-sizing: border-box; background: transparent; border: 1px solid var(--accent); color: var(--accent) !important;">My Profile</a>
          <a href="/logout" class="auth-btn" style="display: block; width: 100%; text-align: center; margin-top: 0; padding: 10px; font-size: 0.75rem; text-decoration: none; box-sizing: border-box; color: white !important;">Logout</a>
        </div>
      </div>
    </div>
  </nav>

  <div class="dashboard-layout">
    <main class="main-content">
      
      <div class="cart-container">
        <h1 style="font-family: var(--font-display); font-size: 2.5rem; margin-bottom: 32px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 24px;">Shopping Cart</h1>
        
        {% if cart_items %}
          <div style="display: flex; flex-direction: column; gap: 24px; margin-bottom: 40px;">
            {% for item in cart_items %}
            <div style="display: flex; gap: 24px; padding: 24px; border: 1px solid var(--border-subtle); border-radius: 8px; background: var(--bg-secondary); align-items: center;">
              <img src="/static/uploads/{{ item.asset.image_filename }}" alt="{{ item.asset.name }}" onerror="this.src='/static/images/product-1.png'" style="width: 120px; height: 120px; object-fit: cover; border-radius: 4px;">
              <div style="flex: 1;">
                <h3 style="font-size: 1.2rem; margin: 0 0 8px 0;"><a href="/buyer/asset/{{ item.asset.id }}" style="color: var(--text-primary); text-decoration: none;">{{ item.asset.name }}</a></h3>
                <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 4px;">Category: {{ item.asset.category }}</div>
                {% if item.variation %}
                <div style="color: var(--accent); font-size: 0.9rem; margin-bottom: 8px;">Variation: {{ item.variation }}</div>
                {% endif %}
                <div style="font-weight: 600; color: var(--accent-light);">₱{{ "{:,.2f}".format(item.asset.price) }} x {{ item.quantity }}</div>
              </div>
              <div style="text-align: right; display: flex; flex-direction: column; justify-content: space-between; height: 120px;">
                <div style="font-size: 1.5rem; font-weight: bold;">₱{{ "{:,.2f}".format(item.asset.price * item.quantity) }}</div>
                <form action="/buyer/cart/remove/{{ item.id }}" method="POST">
                  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                  <button type="submit" class="auth-btn" style="width: auto; padding: 8px 16px; margin: 0; background: transparent; border: 1px solid #ff4444; color: #ff4444; font-size: 0.8rem;">Remove</button>
                </form>
              </div>
            </div>
            {% endfor %}
          </div>
          
          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--border-subtle); padding-top: 32px;">
            <div style="font-size: 1.2rem; color: var(--text-secondary);">Subtotal ({{ cart_items|length }} items)</div>
            <div style="font-size: 2rem; font-weight: bold; color: var(--accent-light);">₱{{ "{:,.2f}".format(total_price) }}</div>
          </div>
          
          <div style="display: flex; justify-content: flex-end; margin-top: 32px;">
            <a href="/buyer/checkout" class="auth-btn" style="width: auto; padding: 16px 48px; text-decoration: none; font-size: 1.1rem; text-align: center;">Proceed to Checkout</a>
          </div>
        {% else %}
          <div style="text-align: center; padding: 60px 20px;">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.5; margin-bottom: 24px; color: var(--text-secondary);"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
            <h2 style="font-size: 1.5rem; margin-bottom: 16px; color: var(--text-primary);">Your cart is empty</h2>
            <p style="color: var(--text-secondary); margin-bottom: 32px;">Looks like you haven't added anything to your cart yet.</p>
            <a href="/buyer/marketplace" class="auth-btn" style="width: auto; padding: 12px 32px; text-decoration: none;">Continue Shopping</a>
          </div>
        {% endif %}
      </div>
      
    </main>
  </div>

  <script src="/static/theme.js"></script>
</body>
</html>"""

with open('templates/buyer/cart.html', 'w', encoding='utf-8') as f:
    f.write(cart_html)
