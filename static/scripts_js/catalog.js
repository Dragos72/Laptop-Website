// catalog.js

// Function to handle the search functionality
function searchLaptops() {
  const searchTerm = document.getElementById('search').value;
  console.log("Searching for:", searchTerm);
}

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



// Call loadCategories when the page loads
document.addEventListener('DOMContentLoaded', loadCategories);

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
