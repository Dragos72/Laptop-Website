// Function to load cart items from the backend
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

// Function to add a laptop to the cart
async function addToCart(laptopId) {
  try {
    const response = await fetch('/add_to_cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ laptop_id: laptopId })
    });
    const data = await response.json();

    if (data.success) {
      alert(data.message);
      loadCartItems(); // Reload cart items to update the quantity and total
    } else {
      alert('Failed to add item to cart: ' + data.message);
    }
  } catch (error) {
    console.error('Error adding item to cart:', error);
    alert('An unexpected error occurred while adding the item to the cart.');
  }
}

// Call loadCartItems when the page loads
document.addEventListener('DOMContentLoaded', loadCartItems);

// Redirect to payment page
function submitOrder() {
  window.location.href = "/payment";
}

  
  // Call loadCartItems when the page loads
  document.addEventListener('DOMContentLoaded', loadCartItems);
  

  async function submitOrder() {
    try {
      const totalPriceElement = document.getElementById('total-price');
      const totalAmount = parseFloat(totalPriceElement.innerText.replace('Total: ', '').replace(' Lei', ''));
  
      const response = await fetch('/submit_payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }, // Ensure Content-Type is JSON
        body: JSON.stringify({ total_amount: totalAmount }) // Send total_amount as JSON
      });
  
      const data = await response.json();
      if (data.success) {
        alert('Order submitted successfully!');
        window.location.href = '/catalog'; // Redirect to catalog
      } else {
        alert('Failed to submit order: ' + data.message);
      }
    } catch (error) {
      console.error('Error submitting order:', error);
      alert('An unexpected error occurred while submitting the order.');
    }
  }
  
  
  
  // Load cart items on page load
  document.addEventListener('DOMContentLoaded', loadCartItems);