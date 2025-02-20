document.getElementById('submit').addEventListener('click', submitQuestion);
document.getElementById('prompt').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        submitQuestion();
    }
});

function submitQuestion() {
    const prompt = document.getElementById('prompt').value;

    if (prompt.trim() === "") {
        alert("Please enter a prompt.");
        return;
    }

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(response => response.json())
    .then(data => {
        const responseDiv = document.getElementById('response');
        if (data.response) {
            responseDiv.innerText = data.response;
            document.getElementById('newQuestion').style.display = 'block'; // Show the new question button
        } else {
            responseDiv.innerText = "Error: " + data.error;
        }
    })
    .catch(error => {
        document.getElementById('response').innerText = "Error: " + error;
    });
}

document.getElementById('newQuestion').addEventListener('click', function() {
    document.getElementById('prompt').value = ''; // Clear the textarea
    document.getElementById('response').innerText = ''; // Clear the response
    this.style.display = 'none'; // Hide the button
});
