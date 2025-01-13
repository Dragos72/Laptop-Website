document.addEventListener("DOMContentLoaded", () => {
    // Add User Form
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
  
    // Remove User Form
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
  
    // Modify User Form
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
  
    // Add Category Form
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

  
    // Add Laptop Form
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
  
    // Remove Laptop Form
  });
  

function removeLaptopByName() {
    const modelName = document.getElementById('laptopNameInput').value.trim(); // Fetch input value

    if (!modelName) {
        alert('Please enter a valid laptop name.');
        return;
    }

    fetch('/admin/remove_laptop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Specify JSON format
        },
        body: JSON.stringify({ ModelName: modelName }), // Send data as JSON
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message); // Success feedback
            } else {
                console.error(data.message);
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An unexpected error occurred.');
        });
}

async function executeQuery(queryName) {
    try {
      const response = await fetch(`/admin/execute_query/${queryName}`);
      const data = await response.json();
  
      if (data.success) {
        const resultsTable = document.getElementById('results-table');
        resultsTable.innerHTML = ''; // Clear previous results
  
        // Create table headers
        if (data.results.length > 0) {
          const headers = Object.keys(data.results[0]);
          const headerRow = document.createElement('tr');
          headers.forEach(header => {
            const th = document.createElement('th');
            th.innerText = header;
            headerRow.appendChild(th);
          });
          resultsTable.appendChild(headerRow);
  
          // Populate table rows
          data.results.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
              const td = document.createElement('td');
              td.innerText = value;
              tr.appendChild(td);
            });
            resultsTable.appendChild(tr);
          });
        } else {
          resultsTable.innerHTML = '<tr><td>No results found</td></tr>';
        }
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Error executing query:', error);
    }
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    const querySelect = document.getElementById("query-select");
    const queryInputContainer = document.getElementById("query-input-container");
    const queryInputLabel = document.getElementById("query-input-label");
    const queryInput = document.getElementById("query-input");
    const executeQueryButton = document.getElementById("execute-query-button");
  
    const queryLabels = {
      laptops_by_brand: "Enter Brand Name",
      users_by_cart_count: "Enter Minimum Cart Count",
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
      const selectedQuery = querySelect.value;
      queryInputLabel.innerText = queryLabels[selectedQuery] || "Enter Parameter";
      queryInputContainer.style.display = queryLabels[selectedQuery] ? "block" : "none";
      executeQueryButton.style.display = "block";
    });
  
    executeQueryButton.addEventListener("click", async () => {
      const selectedQuery = querySelect.value;
      const parameter = queryInput.value.trim();
  
      try {
        const response = await fetch(`/admin/execute_query/${selectedQuery}?param=${parameter}`);
        const data = await response.json();
  
        if (data.success) {
          const resultsTable = document.getElementById("results-table");
          resultsTable.innerHTML = "";
  
          if (data.results.length > 0) {
            const headers = Object.keys(data.results[0]);
            const headerRow = document.createElement("tr");
            headers.forEach((header) => {
              const th = document.createElement("th");
              th.innerText = header;
              headerRow.appendChild(th);
            });
            resultsTable.appendChild(headerRow);
  
            data.results.forEach((row) => {
              const tr = document.createElement("tr");
              Object.values(row).forEach((value) => {
                const td = document.createElement("td");
                td.innerText = value;
                tr.appendChild(td);
              });
              resultsTable.appendChild(tr);
            });
          } else {
            resultsTable.innerHTML = "<tr><td>No results found</td></tr>";
          }
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error("Error executing query:", error);
      }
    });
  });
  
  