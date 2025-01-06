// Show selected address details
function showAddressDetails(type) {
    const select = document.getElementById(`${type}-address`);
    const selectedStreet = select.value;

    if (!selectedStreet) {
        document.getElementById(`${type}-details`).innerHTML = '';
        return;
    }

    fetch(`/get_address_details_by_street/${selectedStreet}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display the address details
                const details = `
                    <p><strong>Street:</strong> ${selectedStreet}</p>
                    <p><strong>Number:</strong> ${data.address.Number}</p>
                    <p><strong>City:</strong> ${data.address.City}</p>
                    <p><strong>Postal Code:</strong> ${data.address.PostalCode}</p>
                    <p><strong>Country:</strong> ${data.address.Country}</p>
                `;
                document.getElementById(`${type}-details`).innerHTML = details;
            } else {
                document.getElementById(`${type}-details`).innerHTML =
                    '<p>Address details not found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching address details:', error);
        });
}

  