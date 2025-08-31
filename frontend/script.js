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
    loadContestants();
    updateVotingStatus();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update status every minute
    setInterval(updateVotingStatus, 60000);
}

function setupEventListeners() {
    // Ticket validation
    document.getElementById('validateTicket').addEventListener('click', validateTicket);
    
    // Vote submission
    document.getElementById('submitVote').addEventListener('click', submitVote);
    
    // Enter key in ticket input
    document.getElementById('ticketCode').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            validateTicket();
        }
    });
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
            showTicketInvalid(data.error);
        }
    } catch (error) {
        showError('Failed to validate ticket. Please try again.');
        console.error('Validation error:', error);
    }
}

function showTicketValid(ticketCode) {
    const statusDiv = document.getElementById('ticketStatus');
    statusDiv.innerHTML = `
        <div class="ticket-status valid">
            <strong>✓ Valid Ticket!</strong><br>
            Ticket code: ${ticketCode}
        </div>
    `;
    statusDiv.classList.remove('hidden');
    
    // Show contestant selection
    document.getElementById('contestantSelection').classList.remove('hidden');
    
    // Enable submit button if contestant is selected
    updateSubmitButton();
}

function showTicketInvalid(error) {
    const statusDiv = document.getElementById('ticketStatus');
    statusDiv.innerHTML = `
        <div class="ticket-status invalid">
            <strong>✗ Invalid Ticket</strong><br>
            ${error}
        </div>
    `;
    statusDiv.classList.remove('hidden');
    
    // Hide contestant selection
    document.getElementById('contestantSelection').classList.add('hidden');
    
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
    submitButton.disabled = !(currentTicketCode && selectedContestantId);
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
    document.getElementById('ticketCode').value = '';
    document.getElementById('ticketStatus').classList.add('hidden');
    document.getElementById('contestantSelection').classList.add('hidden');
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
        showError('Failed to load contestants');
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
    document.getElementById('votedContestant').textContent = contestantName;
    document.getElementById('successModal').classList.remove('hidden');
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorModal').classList.remove('hidden');
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
        // Implement reset voting functionality
        console.log('Resetting voting...');
    }
}

function generateNewTickets() {
    if (confirm('Generate new tickets? This will invalidate all existing tickets.')) {
        // Implement ticket generation
        console.log('Generating new tickets...');
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
