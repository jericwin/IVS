with open('templates/profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

change_password_html = '''
      <section class="profile-section" style="margin-top: 40px;">
        <div class="profile-section-header">
          <h2 class="profile-section-title">Change Password</h2>
          <p class="profile-section-subtitle">Update your account password securely using an email OTP.</p>
        </div>

        <div id="cp-step-1">
          <button id="btn-request-otp" type="button" class="auth-btn" style="width: auto; padding: 12px 32px; margin: 0;">Request OTP to Email</button>
        </div>

        <div id="cp-step-2" style="display: none;">
          <div class="profile-form-row">
            <div class="profile-form-label">OTP Code</div>
            <input type="text" id="cp-otp" class="profile-form-input" placeholder="Enter 6-digit code">
          </div>
          <div class="profile-form-row">
            <div class="profile-form-label">New Password</div>
            <input type="password" id="cp-new-password" class="profile-form-input" placeholder="Enter new password">
          </div>
          <div class="profile-submit-row">
            <div class="profile-submit-label"></div>
            <button id="btn-verify-otp" type="button" class="auth-btn" style="width: auto; padding: 12px 32px; margin: 0;">Confirm Change Password</button>
          </div>
        </div>
      </section>

      <script>
        document.getElementById('btn-request-otp').addEventListener('click', async () => {
          const btn = document.getElementById('btn-request-otp');
          btn.disabled = true;
          btn.innerText = 'Requesting...';
          try {
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            const resp = await fetch('/profile/change-password/request-otp', { 
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken }
            });
            const data = await resp.json();
            if (data.success) {
              alert('OTP sent to your email!');
              document.getElementById('cp-step-1').style.display = 'none';
              document.getElementById('cp-step-2').style.display = 'block';
            } else {
              alert(data.message || 'Error sending OTP');
              btn.disabled = false;
              btn.innerText = 'Request OTP to Email';
            }
          } catch(e) {
            alert('An error occurred.');
            btn.disabled = false;
            btn.innerText = 'Request OTP to Email';
          }
        });

        document.getElementById('btn-verify-otp').addEventListener('click', async () => {
          const btn = document.getElementById('btn-verify-otp');
          const otp = document.getElementById('cp-otp').value;
          const new_password = document.getElementById('cp-new-password').value;
          if(!otp || !new_password) return alert('Please fill in both fields.');
          
          btn.disabled = true;
          btn.innerText = 'Verifying...';
          try {
            const formData = new FormData();
            formData.append('otp', otp);
            formData.append('new_password', new_password);
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            const resp = await fetch('/profile/change-password/verify', { 
                method: 'POST', 
                body: formData,
                headers: { 'X-CSRFToken': csrfToken }
            });
            const data = await resp.json();
            if (data.success) {
              alert('Password changed successfully!');
              window.location.reload();
            } else {
              alert(data.message || 'Error verifying OTP');
              btn.disabled = false;
              btn.innerText = 'Confirm Change Password';
            }
          } catch(e) {
            alert('An error occurred.');
            btn.disabled = false;
            btn.innerText = 'Confirm Change Password';
          }
        });
      </script>
'''

if 'Change Password' not in content:
    content = content.replace('</main>', change_password_html + '\n    </main>')
    with open('templates/profile.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated profile.html')
else:
    print('Already updated profile.html')
