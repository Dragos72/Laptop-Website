function createAccount() {
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const phoneNumber = document.getElementById('phone_number').value;
  
    // Verify that passwords match
    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      return;
    }
  
    // Send data to Flask
    fetch('/create_user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
        phone_number: phoneNumber
      }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert("Account created successfully!");
        window.location.href = "/"; // Redirect to root page
      } else {
        alert("Error: " + data.message);
      }
    })
    .catch(error => console.error('Error:', error));
  }