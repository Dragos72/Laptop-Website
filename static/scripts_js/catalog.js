// catalog.js

// Function to handle the search functionality


// Function to toggle the category dropdown
function toggleDropdown() {
  document.getElementById("categoryDropdown").classList.toggle("show");
}

// Function to load categories from the backend
/*function loadCategories() {
  const categories = ["Laptops", "Accessories", "Chargers"]; // Example categories
  const dropdownContent = document.getElementById('categoryDropdown');

  categories.forEach(category => {
    const a = document.createElement('a');
    a.innerText = category;
    a.href = "#"; // This can be updated to link to the category page
    dropdownContent.appendChild(a);
  });
}
*/
/*
function loadCategories() {
  const dropdownContent = document.getElementById('categoryDropdown');

  // Fetch categories from the backend
  fetch('/get_categories')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        data.categories.forEach(category => {
          const a = document.createElement('a');
          a.innerText = category;
          a.href = "#"; // Update with actual links if needed
          dropdownContent.appendChild(a);
        });
      } else {
        console.error("Failed to load categories:", data.message);
      }
    })
    .catch(error => {
      console.error("Error fetching categories:", error);
    });
}
*/

function loadCategories() {
  fetch('/get_categories', {
    method: 'GET',
    headers: {
      'X-Requested-With': 'XMLHttpRequest' // Custom header
    }
  })
  .then(response => response.json())
  .then(categories => {
    const dropdownContent = document.getElementById('categoryDropdown');
    dropdownContent.innerHTML = ''; // Clear any previous items

    categories.forEach(category => {
      const a = document.createElement('a');
      a.innerText = category;
      a.href = "#";
      a.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default anchor behavior
        filterLaptopsByCategory(category); // Call your function
      });
      dropdownContent.appendChild(a);
    });
  })
  .catch(error => console.error('Error:', error));
}


function displayLaptops(laptops) {
  const laptopList = document.getElementById('laptop-list');
  laptopList.innerHTML = ''; // Clear previous content

  laptops.forEach(laptop => {
    const laptopCard = document.createElement('div');
    laptopCard.classList.add('laptop-card');

    // Make the card clickable
    laptopCard.addEventListener('click', () => {
      window.location.href = `/laptop/${laptop.LaptopID}`;
    });

    // Image
    const img = document.createElement('img');
    const imagePath = `/static/assets/laptop_pictures/${laptop.LaptopID}.jpg`;
    img.src = imagePath;
    img.alt = laptop.ModelName;
    img.onerror = () => {
      img.src = '/static/assets/laptop_pictures/default.jpg';
    };
    laptopCard.appendChild(img);

    // Name
    const modelName = document.createElement('h4');
    modelName.innerText = laptop.ModelName;
    laptopCard.appendChild(modelName);

    // Price
    const price = document.createElement('p');
    price.innerText = `Price: ${laptop.Price} Lei`;
    laptopCard.appendChild(price);

    // Add to cart button (prevent card click redirect)
    const button = document.createElement('button');
    button.innerText = 'Add to Cart';
    button.addEventListener('click', (event) => {
      event.stopPropagation(); // prevent the click from triggering redirect
      addToCart(laptop.LaptopID);
    });
    laptopCard.appendChild(button);

    laptopList.appendChild(laptopCard);
  });
}




// Function to handle adding a laptop to the cart
async function addToCart(laptopId) {
  try {
    const response = await fetch('/add_to_cart', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ laptop_id: laptopId }), // Pass LaptopID in the request body
    });

    const data = await response.json();
    if (data.success) {
      alert('Laptop added to cart successfully!');
    } else {
      alert('Failed to add laptop to cart: ' + data.message);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An unexpected error occurred. Please try again.');
  }
}

async function searchLaptops() {
  const searchTerm = document.getElementById('search').value.trim();
  console.log("Searching for2:", searchTerm);

  try {
    const response = await fetch('/search_laptops', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ search_term: searchTerm }),
    });

    const data = await response.json();
    console.log(data);
    if (data.success) {
      displayLaptops(data.laptops); // Pass the filtered laptops to the display function
    } else {
      console.error('Error searching laptops:', data.message);
      alert('Failed to search laptops. Please try again.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An unexpected error occurred. Please try again.');
  }
}

async function handleAutocomplete() {
  const input = document.getElementById('search');
  const list = document.getElementById('autocomplete-list');
  const term = input.value.trim();

  list.innerHTML = ''; // clear old results

  if (term.length === 0) return;

  try {
    const res = await fetch(`/autocomplete_laptops?term=${encodeURIComponent(term)}`);
    const suggestions = await res.json();

    suggestions.forEach(name => {
      const li = document.createElement('li');
      li.textContent = name;
      li.onclick = () => {
        input.value = name;
        list.innerHTML = '';
        searchLaptops(); // trigger full search
      };
      list.appendChild(li);
    });
  } catch (error) {
    console.error('Autocomplete error:', error);
  }
}

// Optional: Close suggestion box on outside click
document.addEventListener('click', function(e) {
  if (!document.querySelector('.search-bar').contains(e.target)) {
    document.getElementById('autocomplete-list').innerHTML = '';
  }
});



document.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await fetch('/get_laptops');
    const laptops = await response.json();
    displayLaptops(laptops); // Display all laptops
  } catch (error) {
    console.error('Error fetching laptops:', error);
  }
});

// Call loadCategories when the page loads
document.addEventListener('DOMContentLoaded', loadCategories);
document.addEventListener('DOMContentLoaded', displayLaptops);

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let i = 0; i < dropdowns.length; i++) {
      const openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

function filterLaptopsByCategory(categoryName) {
  fetch('/filter_laptops', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
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
  .catch(error => {
    console.error("Error filtering laptops:", error);
  });
}