/*function login() {
    // This function currently redirects to a placeholder HTML page
    window.location.href = "/mainPage"; // Redirects to a 'welcome.html' page after login
  }
*/
function login() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        window.location.href = data.redirect; // Redirect based on response
      } else {
        alert("Login failed: " + data.message);
      }
    })
    .catch(error => console.error('Error:', error));
}


function route_createAccount() {
  window.location.href = "/create_account";
}
