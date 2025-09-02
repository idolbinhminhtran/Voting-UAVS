// Global variables
let selectedContestantId = null;
let currentTicketCode = null;
let contestants = [];

// API endpoints
const API_BASE = '/api';
const ENDPOINTS = {
    VOTE: `${API_BASE}/vote`,
    RESULTS: `${API_BASE}/results`,
    CONTESTANTS: `${API_BASE}/contestants`,
    VALIDATE_TICKET: `${API_BASE}/ticket/validate`
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Only load contestants and update status if we're on a page that needs them
    if (document.getElementById('contestantsList') || document.getElementById('contestantsGrid')) {
        loadContestants();
    }
    
    if (document.getElementById('statusText')) {
        updateVotingStatus();
        // Update status every minute
        setInterval(updateVotingStatus, 60000);
    }
    
    // Set up event listeners only if elements exist
    setupEventListeners();
}

function setupEventListeners() {
    // Ticket validation - only if elements exist
    const validateButton = document.getElementById('validateTicket');
    if (validateButton) {
        validateButton.addEventListener('click', validateTicket);
    }
    
    // Vote submission - only if elements exist
    const submitButton = document.getElementById('submitVote');
    if (submitButton) {
        submitButton.addEventListener('click', submitVote);
    }
    
    // Enter key in ticket input - only if element exists
    const ticketInput = document.getElementById('ticketCode');
    if (ticketInput) {
        ticketInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                validateTicket();
            }
        });
    }
}

// Ticket validation
async function validateTicket() {
    const ticketCode = document.getElementById('ticketCode').value.trim();
    
    if (!ticketCode) {
        showError('Please enter a ticket code');
        return;
    }
    
    try {
        const response = await fetch(ENDPOINTS.VALIDATE_TICKET, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ticket_code: ticketCode })
        });
        
        const data = await response.json();
        
        if (data.valid) {
            showTicketValid(ticketCode);
            currentTicketCode = ticketCode;
        } else {
            showTicketInvalid(data.error || 'Invalid ticket or already used');
        }
    } catch (error) {
        showError('Failed to validate ticket. Please try again.');
        console.error('Validation error:', error);
    }
}

function showTicketValid(ticketCode) {
    const statusDiv = document.getElementById('ticketStatus');
    if (!statusDiv) return;
    
    statusDiv.innerHTML = `
        <div class="ticket-status valid">
            <strong>✓ Valid Ticket!</strong><br>
            Ticket code: ${ticketCode}
        </div>
    `;
    statusDiv.classList.remove('hidden');
    
    // Show contestant selection
    const contestantSelection = document.getElementById('contestantSelection');
    if (contestantSelection) {
        contestantSelection.classList.remove('hidden');
    }
    
    // Enable submit button if contestant is selected
    updateSubmitButton();
}

function showTicketInvalid(error) {
    const statusDiv = document.getElementById('ticketStatus');
    if (!statusDiv) return;
    
    statusDiv.innerHTML = `
        <div class="ticket-status invalid">
            <strong>✗ Invalid Ticket</strong><br>
            ${error}
        </div>
    `;
    statusDiv.classList.remove('hidden');
    
    // Hide contestant selection
    const contestantSelection = document.getElementById('contestantSelection');
    if (contestantSelection) {
        contestantSelection.classList.add('hidden');
    }
    
    // Clear any previous selection
    selectedContestantId = null;
    currentTicketCode = null;
    updateSubmitButton();
}

// Contestant selection
function selectContestant(contestantId) {
    selectedContestantId = contestantId;
    
    // Update UI to show selection
    document.querySelectorAll('.contestant-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    event.currentTarget.classList.add('selected');
    
    // Enable submit button
    updateSubmitButton();
}

function updateSubmitButton() {
    const submitButton = document.getElementById('submitVote');
    if (submitButton) {
        submitButton.disabled = !(currentTicketCode && selectedContestantId);
    }
}

// Vote submission
async function submitVote() {
    if (!currentTicketCode || !selectedContestantId) {
        showError('Please select a contestant first');
        return;
    }
    
    try {
        const response = await fetch(ENDPOINTS.VOTE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticket_code: currentTicketCode,
                contestant_id: selectedContestantId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.contestant_name);
            resetVotingForm();
        } else {
            showError(data.error || 'Failed to submit vote');
        }
    } catch (error) {
        showError('Failed to submit vote. Please try again.');
        console.error('Vote submission error:', error);
    }
}

function resetVotingForm() {
    const ticketInput = document.getElementById('ticketCode');
    if (ticketInput) {
        ticketInput.value = '';
    }
    
    const statusDiv = document.getElementById('ticketStatus');
    if (statusDiv) {
        statusDiv.classList.add('hidden');
    }
    
    const contestantSelection = document.getElementById('contestantSelection');
    if (contestantSelection) {
        contestantSelection.classList.add('hidden');
    }
    
    selectedContestantId = null;
    currentTicketCode = null;
    
    // Clear contestant selection
    document.querySelectorAll('.contestant-card').forEach(card => {
        card.classList.remove('selected');
    });
}

// Load contestants
async function loadContestants() {
    try {
        const response = await fetch(ENDPOINTS.CONTESTANTS);
        contestants = await response.json();
        
        displayContestants(contestants);
    } catch (error) {
        console.error('Failed to load contestants:', error);
        // Only show error if we're on a page that displays contestants
        if (document.getElementById('contestantsList') || document.getElementById('contestantsGrid')) {
            showError('Failed to load contestants');
        }
    }
}

function displayContestants(contestants) {
    const container = document.getElementById('contestantsList');
    
    if (!container) return; // Not on main voting page
    
    container.innerHTML = contestants.map(contestant => `
        <div class="contestant-card" onclick="selectContestant(${contestant.id})">
            <img src="${contestant.image_url || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iMzUiIHI9IjE1IiBmaWxsPSIjOUI5QkEwIi8+CjxyZWN0IHg9IjMwIiB5PSI1NSIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjOUI5QkEwIi8+Cjwvc3ZnPgo='}" 
                 alt="${contestant.name}" 
                 onerror="this.style.display='none'">
            <h4>${contestant.name}</h4>
            <p>${contestant.description || 'No description available'}</p>
        </div>
    `).join('');
}



// Voting status
function updateVotingStatus() {
    const now = new Date();
    const currentTime = now.toLocaleString();
    const currentHour = now.getHours();
    
    // Check if voting is open (24 hours)
    const votingOpen = true;
    
    updateVotingStatusDisplay(votingOpen, currentTime);
}

function updateVotingStatusDisplay(votingOpen, currentTime) {
    const statusText = document.getElementById('statusText');
    const currentTimeSpan = document.getElementById('currentTime');
    
    if (statusText) {
        statusText.textContent = votingOpen ? 'Voting is OPEN' : 'Voting is CLOSED';
        statusText.className = votingOpen ? 'status-open' : 'status-closed';
    }
    
    if (currentTimeSpan) {
        currentTimeSpan.textContent = new Date(currentTime).toLocaleString();
    }
}

// Load results (for admin panel)
async function loadResults() {
    try {
        const response = await fetch(ENDPOINTS.RESULTS);
        const data = await response.json();
        
        displayResults(data.results);
        updateVotingStatusDisplay(data.voting_open, data.current_time);
    } catch (error) {
        console.error('Failed to load results:', error);
        showError('Failed to load results');
    }
}

function displayResults(results) {
    const container = document.getElementById('resultsContainer') || 
                     document.getElementById('resultsContainerAdmin');
    
    if (!container) return;
    
    if (results.length === 0) {
        container.innerHTML = '<div class="loading">No results available</div>';
        return;
    }
    
    // Find winner (highest votes)
    const maxVotes = Math.max(...results.map(r => r.vote_count));
    
    container.innerHTML = results.map((result, index) => {
        const isWinner = result.vote_count === maxVotes && maxVotes > 0;
        const percentage = results.reduce((sum, r) => sum + r.vote_count, 0) > 0 
            ? (result.vote_count / results.reduce((sum, r) => sum + r.vote_count, 0) * 100).toFixed(1)
            : '0.0';
        
        return `
            <div class="result-card ${isWinner ? 'winner' : ''}">
                <div class="result-header">
                    <h3>${result.name}</h3>
                    ${isWinner ? '<span class="winner-badge">🏆 Winner</span>' : ''}
                </div>
                <div class="result-stats">
                    <div class="vote-count">
                        <span class="number">${formatNumber(result.vote_count)}</span>
                        <span class="label">votes</span>
                    </div>
                    <div class="percentage">
                        <span class="number">${percentage}%</span>
                        <span class="label">of total</span>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

// Modal functions
function showSuccess(contestantName) {
    const votedContestant = document.getElementById('votedContestant');
    const successModal = document.getElementById('successModal');
    
    if (votedContestant && successModal) {
        votedContestant.textContent = contestantName;
        successModal.classList.remove('hidden');
    }
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorModal = document.getElementById('errorModal');
    
    if (errorMessage && errorModal) {
        errorMessage.textContent = message;
        errorModal.classList.remove('hidden');
    } else {
        // Fallback: use console or alert if modals don't exist
        console.error('Error:', message);
        alert('Error: ' + message);
    }
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.add('hidden');
    });
}

// Admin functions (if on admin page)
function loadDashboardData() {
    // This function is called from admin.html
    loadResults();
    loadTicketStats();
}

function loadTicketStats() {
    // Placeholder for ticket statistics
    // This would need to be implemented based on your backend
    console.log('Loading ticket statistics...');
}

function confirmResetVoting() {
    if (confirm('Are you sure you want to reset all voting? This action cannot be undone.')) {
        fetch('/api/admin/reset-voting', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Voting has been reset successfully!');
                // Reload the dashboard data
                if (typeof loadDashboardData === 'function') {
                    loadDashboardData();
                }
            } else {
                alert('Error: ' + (data.error || 'Failed to reset voting'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error: Failed to reset voting');
        });
    }
}

function generateNewTickets() {
    const count = prompt('How many tickets to generate? (default: 100)', '100');
    if (count === null) return; // User cancelled
    
    const ticketCount = parseInt(count) || 100;
    
    if (confirm(`Generate ${ticketCount} new tickets? This will add to existing tickets.`)) {
        fetch('/api/admin/generate-tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ count: ticketCount }),
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Successfully generated ${data.count} new tickets!`);
                // Reload the dashboard data
                if (typeof loadDashboardData === 'function') {
                    loadDashboardData();
                }
            } else {
                alert('Error: ' + (data.error || 'Failed to generate tickets'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error: Failed to generate tickets');
        });
    }
}

function addContestant(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const contestantData = {
        name: formData.get('contestantName'),
        description: formData.get('contestantDescription'),
        image_url: formData.get('contestantImage')
    };
    
    // Implement contestant addition
    console.log('Adding contestant:', contestantData);
}

// Utility functions
function formatNumber(num) {
    return num.toLocaleString();
}

function formatPercentage(num) {
    return num.toFixed(1);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showError('An unexpected error occurred');
});

// Close modals when clicking outside
window.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        closeModal();
    }
});
