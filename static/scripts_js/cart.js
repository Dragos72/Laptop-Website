// Function to load cart items from the backend
async function loadCartItems() {
    try {
      const response = await fetch('/get_cart_items'); // Fetch data from the backend
      const data = await response.json();
  
      if (data.success) {
        const cartItems = data.items;
        const cartContainer = document.getElementById('cart-items');
        cartContainer.innerHTML = ''; // Clear previous content
  
        let totalPrice = 0;
  
        cartItems.forEach(item => {
          // Create cart item element
          const cartItem = document.createElement('div');
          cartItem.classList.add('cart-item');
  
          // Display laptop details
          const itemDetails = document.createElement('div');
          itemDetails.innerHTML = `
            <h4>${item.model_name}</h4>
            <p>Price: ${item.price} Lei</p>
            <p>Quantity: ${item.quantity}</p>
          `;
          cartItem.appendChild(itemDetails);
  
          // Add the total price calculation
          totalPrice += item.price * item.quantity;
  
          // Append to the cart container
          cartContainer.appendChild(cartItem);
        });
  
        // Update total price
        const totalPriceElement = document.getElementById('total-price');
        totalPriceElement.innerText = `Total: ${totalPrice.toFixed(2)} Lei`;
      } else {
        alert('Failed to load cart items: ' + data.message);
      }
    } catch (error) {
      console.error('Error loading cart items:', error);
      alert('An unexpected error occurred while loading the cart.');
    }
  }
  
  // Call loadCartItems when the page loads
  document.addEventListener('DOMContentLoaded', loadCartItems);
  

  function submitOrder() {
    window.location.href = "/payment"; // Redirect to the payment page
  }
  
  // Load cart items on page load
  document.addEventListener('DOMContentLoaded', loadCartItems);