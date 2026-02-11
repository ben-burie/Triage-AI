const questionInput = document.getElementById('question');
const submitBtn = document.getElementById('submitBtn');
const responseSection = document.getElementById('responseSection');
const responseContent = document.getElementById('responseContent');
const ticketList = document.getElementById('ticketList');

submitBtn.addEventListener('click', handleSubmit);
questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        handleSubmit();
    }
});

function handleSubmit() {
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter a question');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    responseSection.classList.add('visible');
    responseContent.innerHTML = '<div class="loading">Analyzing your question</div>';
    ticketList.innerHTML = '';

    fetch('/api/question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const responseData = {
            answer: data.answer,
            tickets: data.tickets || []
        };
        displayResponse(responseData);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit';
    })
    .catch(error => {
        console.error('Error:', error);
        responseContent.innerHTML = '<div style="color: #dc3545;">An error occurred while processing your request. Please try again.</div>';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit';
    });
}

function displayResponse(data) {
    let answer = data.answer;
    let tickets = data.tickets || [];

    answer = answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    answer = answer.replace(/\n/g, '<br>');

    responseContent.innerHTML = answer;

    if (tickets && tickets.length > 0) {
        ticketList.innerHTML = tickets.map(ticket => `
            <li class="ticket-item">
                <a class="ticket-link">${ticket.ticket_id}: ${ticket.issue}</a>
                <div class="ticket-meta">${ticket.resolution}</div>
            </li>
        `).join('');
    } else {
        ticketList.innerHTML = '<li class="ticket-item" style="border: none;">No related tickets found</li>';
    }
}