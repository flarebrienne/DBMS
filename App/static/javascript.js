async function delete(url) {
    const confirmed = confirm("Are you sure you want to delete this doctor?");
    if (!confirmed) return;

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const result = await response.json();

        if (result.success) {
            const row = document.getElementById(`doctor-row-${doctorId}`);
            console.log(row);
            if (row) {
                row.classList.add("fade-out");
                setTimeout(() => row.remove(), 300);
            }
        } else {
            alert("Failed to delete doctor: " + result.message);
        }
    } catch (error) {
        alert("An error occurred while deleting the doctor.");
        console.error(error);
    }
}
