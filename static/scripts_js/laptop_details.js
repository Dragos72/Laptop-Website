// --- Add to cart ---
async function addToCart(laptopId) {
    try {
      const response = await fetch('/add_to_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ laptop_id: laptopId })
      });
  
      const data = await response.json();
      if (data.success) {
        alert('Laptop added to cart!');
      } else {
        alert('Failed to add to cart: ' + data.message);
      }
    } catch (error) {
      alert('Error adding to cart.');
    }
  }
  
  // --- Redirect by category ---
  function filterLaptopsByCategory(categoryName) {
    const url = `/catalog?category=${encodeURIComponent(categoryName)}`;
    window.location.href = url;
  }
  
  // --- Redirect by search ---
  function searchLaptops() {
    const searchTerm = document.getElementById('search').value.trim();
    if (searchTerm) {
      const url = `/catalog?search=${encodeURIComponent(searchTerm)}`;
      window.location.href = url;
    }
  }
  
  // --- Autocomplete for search ---
  async function handleAutocomplete() {
    const input = document.getElementById('search');
    const list = document.getElementById('autocomplete-list');
    const term = input.value.trim();
  
    list.innerHTML = '';
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
          searchLaptops();
        };
        list.appendChild(li);
      });
    } catch (error) {
      console.error('Autocomplete error:', error);
    }
  }
  
  // --- Load categories in dropdown ---
  function toggleDropdown() {
    document.getElementById("categoryDropdown").classList.toggle("show");
  }
  
  function loadCategories() {
    fetch('/get_categories', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(res => res.json())
      .then(categories => {
        const dropdown = document.getElementById('categoryDropdown');
        dropdown.innerHTML = '';
        categories.forEach(cat => {
          const a = document.createElement('a');
          a.innerText = cat;
          a.href = '#';
          a.onclick = (e) => {
            e.preventDefault();
            filterLaptopsByCategory(cat);
          };
          dropdown.appendChild(a);
        });
      });
  }
  
  // --- Close autocomplete on outside click ---
  document.addEventListener('click', function (e) {
    if (!document.querySelector('.search-bar').contains(e.target)) {
      document.getElementById('autocomplete-list').innerHTML = '';
    }
  });
  
  document.addEventListener('DOMContentLoaded', loadCategories);
  