document.addEventListener('DOMContentLoaded', loadCartItems);

async function loadCartItems() {
  try {
    const response = await fetch('/get_cart_items');
    const data = await response.json();

    if (!data.success) {
      alert('Failed to load cart: ' + data.message);
      return;
    }

    const cartItems = data.items;
    const cartContainer = document.getElementById('cart-items');
    cartContainer.innerHTML = '';

    let totalPrice = 0;

    cartItems.forEach(item => {
      const cartItem = document.createElement('div');
      cartItem.classList.add('cart-item');
      cartItem.dataset.laptopId = item.laptop_id;

      const img = document.createElement('img');
      img.src = `/static/assets/laptop_pictures/${item.laptop_id}.jpg`;
      img.alt = item.model_name;
      img.onerror = () => img.src = '/static/assets/laptop_pictures/default.jpg';
      img.classList.add('cart-img');

      const info = document.createElement('div');
      info.classList.add('cart-info');
      info.innerHTML = `
        <h4>${item.model_name}</h4>
        <p>Price: ${item.price} Lei</p>
        <p><small>In stock: ${item.stock_quantity}</small></p>
      `;

      const quantityInput = document.createElement('input');
      quantityInput.type = 'number';
      quantityInput.value = item.quantity;
      quantityInput.min = 0;
      quantityInput.max = item.stock_quantity;
      quantityInput.classList.add('qty-input');

      quantityInput.addEventListener('input', () => {
        let qty = parseInt(quantityInput.value) || 0;
        if (qty > item.stock_quantity) {
          qty = item.stock_quantity;
          quantityInput.value = qty;
        }
        item.quantity = qty;
        updateTotal(cartItems);
      });

      const removeBtn = document.createElement('button');
      removeBtn.innerText = 'Remove';
      removeBtn.classList.add('remove-btn');
      removeBtn.onclick = () => removeFromCart(item.laptop_id);

      const rightControls = document.createElement('div');
      rightControls.classList.add('cart-controls');
      rightControls.appendChild(quantityInput);
      rightControls.appendChild(removeBtn);

      cartItem.appendChild(img);
      cartItem.appendChild(info);
      cartItem.appendChild(rightControls);

      cartContainer.appendChild(cartItem);
      totalPrice += item.price * item.quantity;
    });

    updateTotal(cartItems);
  } catch (error) {
    console.error('Error loading cart:', error);
    alert('An unexpected error occurred.');
  }
}

function updateTotal(cartItems) {
  const total = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  document.getElementById('total-price').innerText = `Total: ${total.toFixed(2)} Lei`;
}

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
      loadCartItems();
    } else {
      alert('Failed to add item to cart: ' + data.message);
    }
  } catch (error) {
    console.error('Error adding item to cart:', error);
    alert('An unexpected error occurred while adding the item to the cart.');
  }
}

async function updateCartQuantities(cartItems) {
  try {
    const response = await fetch('/update_cart_quantities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: cartItems })
    });

    const data = await response.json();
    if (!data.success) {
      alert('Failed to update cart quantities: ' + data.message);
    }
  } catch (error) {
    console.error('Error updating quantities:', error);
  }
}

async function submitOrder() {
  try {
    const totalPriceElement = document.getElementById('total-price');
    const totalAmount = parseFloat(totalPriceElement.innerText.replace('Total: ', '').replace(' Lei', ''));

    const cartItems = Array.from(document.querySelectorAll('.cart-item')).map(item => {
      const laptopId = parseInt(item.dataset.laptopId);
      const quantity = parseInt(item.querySelector('.qty-input').value);
      return { laptop_id: laptopId, quantity };
    });

    await updateCartQuantities(cartItems);

    const response = await fetch('/submit_order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ total_amount: totalAmount })
    });

    const data = await response.json();

    if (data.success) {
      alert('Order submitted successfully!');
      window.location.href = '/catalog';
    } else {
      alert('Failed to submit order: ' + data.message);
    }
  } catch (error) {
    console.error('Error submitting order:', error);
    alert('An unexpected error occurred while submitting the order.');
  }
}

async function removeFromCart(laptopId) {
  try {
    const response = await fetch('/remove_from_cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ laptop_id: laptopId })
    });

    const data = await response.json();
    if (data.success) {
      loadCartItems();
    } else {
      alert('Failed to remove item: ' + data.message);
    }
  } catch (error) {
    console.error('Error removing item:', error);
    alert('An error occurred.');
  }
}
