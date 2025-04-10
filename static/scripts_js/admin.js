document.addEventListener("DOMContentLoaded", () => {
  // Add User
  document.getElementById("addUserForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const response = await fetch("/admin/add_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    alert(result.message);
  });

  // Remove User
  document.getElementById("removeUserForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = new FormData(event.target).get("email");
    const response = await fetch("/admin/remove_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const result = await response.json();
    alert(result.message);
  });

  // Modify User
  document.getElementById("modifyUserForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const response = await fetch("/admin/modify_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    alert(result.message);
  });

  // Add Category
  document.getElementById("addCategoryForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const response = await fetch("/admin/add_category", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    alert(result.message);
  });

  // Remove Category
  document.getElementById("removeCategoryForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const categoryName = new FormData(event.target).get("categoryName");
    const response = await fetch("/admin/remove_category", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ categoryName }),
    });
    const result = await response.json();
    alert(result.message);
  });

  // Update Category
  document.getElementById("updateCategoryForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const response = await fetch("/admin/update_category", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    alert(result.message);
  });

  // Add Laptop
  document.getElementById("addLaptopForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    const response = await fetch("/admin/add_laptop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    alert(result.message);
  });
});

// Remove Laptop by ModelName
function removeLaptopByName() {
  const modelName = document.getElementById('laptopNameInput').value.trim();
  if (!modelName) return alert('Please enter a valid laptop name.');

  fetch('/admin/remove_laptop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ModelName: modelName }),
  })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => {
      console.error('Error:', error);
      alert('An unexpected error occurred.');
    });
}

// Query Execution Logic
async function executeQuery(queryName) {
  try {
    const response = await fetch(`/admin/execute_query/${queryName}`);
    const data = await response.json();

    if (!data.success) return alert(data.message);

    const table = document.getElementById('results-table');
    table.innerHTML = '';

    if (data.results.length > 0) {
      const headers = Object.keys(data.results[0]);
      const headerRow = document.createElement('tr');
      headers.forEach(header => {
        const th = document.createElement('th');
        th.innerText = header;
        headerRow.appendChild(th);
      });
      table.appendChild(headerRow);

      data.results.forEach(row => {
        const tr = document.createElement('tr');
        Object.values(row).forEach(value => {
          const td = document.createElement('td');
          td.innerText = value;
          tr.appendChild(td);
        });
        table.appendChild(tr);
      });
    } else {
      table.innerHTML = '<tr><td>No results found</td></tr>';
    }
  } catch (error) {
    console.error('Error executing query:', error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const querySelect = document.getElementById("query-select");
  const inputContainer = document.getElementById("query-input-container");
  const inputLabel = document.getElementById("query-input-label");
  const inputField = document.getElementById("query-input");
  const executeBtn = document.getElementById("execute-query-button");

  const queryLabels = {
    laptops_by_brand: "Enter Brand Name",
    popular_brands: "Enter Minimum Laptops in Brand",
    total_orders_by_user: "Enter Minimum Order Amount",
    popular_categories: "Enter Minimum Laptops in Category",
    total_stock_by_brand: "Enter Brand Name",
    average_price_by_category: "Enter Category Name",
    most_expensive_laptop_by_brand: "Enter Brand Name",
    users_with_high_spending: "Enter Average Spending Threshold",
    laptops_not_in_cart: "Enter Laptop Price",
    categories_with_high_stock: "Enter Stock Threshold",
    no_payment_users: "Enter a Year"
  };

  querySelect.addEventListener("change", () => {
    const selected = querySelect.value;
    inputLabel.innerText = queryLabels[selected] || "Enter Parameter";
    inputContainer.style.display = queryLabels[selected] ? "block" : "none";
    executeBtn.style.display = "block";
  });

  executeBtn.addEventListener("click", async () => {
    const selected = querySelect.value;
    const param = inputField.value.trim();

    try {
      const response = await fetch(`/admin/execute_query/${selected}?param=${param}`);
      const data = await response.json();

      const table = document.getElementById("results-table");
      table.innerHTML = "";

      if (data.success && data.results.length > 0) {
        const headers = Object.keys(data.results[0]);
        const headerRow = document.createElement("tr");
        headers.forEach(header => {
          const th = document.createElement("th");
          th.innerText = header;
          headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        data.results.forEach(row => {
          const tr = document.createElement("tr");
          Object.values(row).forEach(value => {
            const td = document.createElement("td");
            td.innerText = value;
            tr.appendChild(td);
          });
          table.appendChild(tr);
        });
      } else {
        table.innerHTML = "<tr><td>No results found</td></tr>";
      }
    } catch (error) {
      console.error("Error executing query:", error);
    }
  });
});
