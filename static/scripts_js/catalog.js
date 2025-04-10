// Dropdown toggle
function toggleDropdown() {
  document.getElementById("categoryDropdown").classList.toggle("show");
}

// Load categories dynamically from the backend
function loadCategories() {
  fetch('/get_categories', {
    method: 'GET',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(response => response.json())
    .then(categories => {
      const dropdownContent = document.getElementById('categoryDropdown');
      dropdownContent.innerHTML = '';
      categories.forEach(category => {
        const a = document.createElement('a');
        a.innerText = category;
        a.href = "#";
        a.addEventListener('click', (event) => {
          event.preventDefault();
          filterLaptopsByCategory(category);
        });
        dropdownContent.appendChild(a);
      });
    })
    .catch(error => console.error('Error:', error));
}

// Display laptop cards
function displayLaptops(laptops) {
  const laptopList = document.getElementById('laptop-list');
  laptopList.innerHTML = '';

  laptops.forEach(laptop => {
    const laptopCard = document.createElement('div');
    laptopCard.classList.add('laptop-card');
    laptopCard.addEventListener('click', () => {
      window.location.href = `/laptop/${laptop.LaptopID}`;
    });

    const img = document.createElement('img');
    img.src = `/static/assets/laptop_pictures/${laptop.LaptopID}.jpg`;
    img.alt = laptop.ModelName;
    img.onerror = () => img.src = '/static/assets/laptop_pictures/default.jpg';

    const modelName = document.createElement('h4');
    modelName.innerText = laptop.ModelName;

    const price = document.createElement('p');
    price.innerText = `Price: ${laptop.Price} Lei`;

    const button = document.createElement('button');
    button.innerText = 'Add to Cart';
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      addToCart(laptop.LaptopID);
    });

    laptopCard.appendChild(img);
    laptopCard.appendChild(modelName);
    laptopCard.appendChild(price);
    laptopCard.appendChild(button);
    laptopList.appendChild(laptopCard);
  });
}

// Search functionality
async function searchLaptops() {
  const searchTerm = document.getElementById('search').value.trim();
  try {
    const response = await fetch('/search_laptops', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ search_term: searchTerm }),
    });

    const data = await response.json();
    if (data.success) {
      displayLaptops(data.laptops);
    } else {
      alert('Failed to search laptops: ' + data.message);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred while searching.');
  }
}

// Autocomplete suggestion box
async function handleAutocomplete() {
  const input = document.getElementById('search');
  const list = document.getElementById('autocomplete-list');
  const term = input.value.trim();

  list.innerHTML = '';
  if (!term) return;

  try {
    const res = await fetch(`/autocomplete_laptops?term=${encodeURIComponent(term)}`);
    const suggestions = await res.json();

    suggestions.forEach(name => {
      const li = document.createElement('li');
      li.textContent = name;
      li.onclick = () => {
        input.value = name;
        list.innerHTML = '';
        searchLaptops();
      };
      list.appendChild(li);
    });
  } catch (error) {
    console.error('Autocomplete error:', error);
  }
}

// Filter laptops by category
function filterLaptopsByCategory(categoryName) {
  fetch('/filter_laptops', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category_name: categoryName })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        displayLaptops(data.laptops);
      } else {
        alert("Failed to filter laptops: " + data.message);
      }
    })
    .catch(error => console.error("Error filtering laptops:", error));
}

// Add a laptop to the cart
async function addToCart(laptopId) {
  try {
    const response = await fetch('/add_to_cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ laptop_id: laptopId }),
    });

    const data = await response.json();
    if (data.success) {
      alert('Laptop added to cart successfully!');
    } else {
      alert('Failed to add laptop: ' + data.message);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again.');
  }
}

// Close dropdown and autocomplete if clicking outside
document.addEventListener('click', (e) => {
  if (!document.querySelector('.search-bar').contains(e.target)) {
    document.getElementById('autocomplete-list').innerHTML = '';
  }
  if (!e.target.matches('.dropbtn')) {
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let dropdown of dropdowns) {
      dropdown.classList.remove('show');
    }
  }
});

// Load data on page load
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await fetch('/get_laptops');
    const laptops = await response.json();
    displayLaptops(laptops);
  } catch (error) {
    console.error('Error fetching laptops:', error);
  }
  loadCategories();
});
