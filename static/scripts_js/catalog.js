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
      categories.forEach(category => {
          const a = document.createElement('a');
          a.innerText = category;
          a.href = "#";
          dropdownContent.appendChild(a);
      });
  })
  .catch(error => console.error('Error:', error));
}

function displayLaptops(laptops) {
  const laptopList = document.getElementById('laptop-list');
  laptopList.innerHTML = ''; // Clear existing content

  let row;
  laptops.forEach((laptop, index) => {
    // Create a new row every 3 laptops
    if (index % 3 === 0) {
      row = document.createElement('div');
      row.classList.add('row');
      laptopList.appendChild(row);
    }

    // Create the laptop card
    const laptopCard = document.createElement('div');
    laptopCard.classList.add('laptop-card');

    // Set laptop image
    const img = document.createElement('img');
    img.src = laptopImageUrl;
    img.alt = laptop.model_name;
    laptopCard.appendChild(img);

    // Set model name
    const modelName = document.createElement('h4');
    modelName.innerText = laptop.model_name;
    laptopCard.appendChild(modelName);

    // Set price
    const price = document.createElement('p');
    price.innerText = `Price: ${laptop.price} Lei`;
    laptopCard.appendChild(price);

    // Add to cart button
    const button = document.createElement('button');
    button.innerText = 'Add to Cart';
    laptopCard.appendChild(button);

    // Append the laptop card to the row
    row.appendChild(laptopCard);
  });
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
