document.addEventListener('DOMContentLoaded', function () {
  // SIGNUP FORM SUBMIT
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm-password').value;

      if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
      }

      const response = await fetch('/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const result = await response.json();
      alert(result.message || result.error);
    });
  }

  // LOGIN FORM SUBMIT
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;

      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const result = await response.json();
      alert(result.message || result.error);
    });
  }

  // FORM TOGGLE LOGIC
  const signupTab = document.getElementById('signup-tab');
  const loginTab = document.getElementById('login-tab');
  const switchToLogin = document.getElementById('switch-to-login');
  const switchToSignup = document.getElementById('switch-to-signup');

  if (signupTab && loginTab && signupForm && loginForm) {
    signupTab.addEventListener('click', () => {
      signupTab.classList.add('active');
      loginTab.classList.remove('active');
      signupForm.classList.add('active');
      loginForm.classList.remove('active');
    });

    loginTab.addEventListener('click', () => {
      loginTab.classList.add('active');
      signupTab.classList.remove('active');
      loginForm.classList.add('active');
      signupForm.classList.remove('active');
    });
  }

  if (switchToLogin) {
    switchToLogin.addEventListener('click', () => {
      loginTab?.click();
    });
  }

  if (switchToSignup) {
    switchToSignup.addEventListener('click', () => {
      signupTab?.click();
    });
  }
});
