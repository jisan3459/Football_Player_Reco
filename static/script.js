document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('playerSearch');
    const searchResults = document.getElementById('searchResults');
    const searchBtn = document.getElementById('searchBtn');
    
    const loadingIndicator = document.getElementById('loadingIndicator');
    const recommendationsSection = document.getElementById('recommendationsSection');
    const recommendationsGrid = document.getElementById('recommendationsGrid');
    const selectedPlayerName = document.getElementById('selectedPlayerName');
    const errorMessage = document.getElementById('errorMessage');

    let debounceTimer;

    // Search input handler
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();

        if (query.length < 2) {
            searchResults.innerHTML = '';
            searchResults.classList.remove('active');
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    displaySearchResults(data);
                })
                .catch(err => console.error('Search error:', err));
        }, 300);
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            searchResults.classList.remove('active');
        }
    });

    // Handle search button click
    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            getRecommendations(query);
            searchResults.classList.remove('active');
        }
    });

    // Display search results
    function displaySearchResults(results) {
        searchResults.innerHTML = '';
        
        if (results.length === 0) {
            const noRes = document.createElement('div');
            noRes.className = 'search-item';
            noRes.textContent = 'No players found';
            searchResults.appendChild(noRes);
            searchResults.classList.add('active');
            return;
        }

        results.forEach(player => {
            const item = document.createElement('div');
            item.className = 'search-item';
            item.innerHTML = `
                <div class="player-name">${player.name}</div>
                <div class="player-meta">
                    <span>${player.pos}</span>
                    <span>${player.squad}</span>
                </div>
            `;
            
            item.addEventListener('click', () => {
                searchInput.value = player.name;
                searchResults.classList.remove('active');
                getRecommendations(player.name);
            });
            
            searchResults.appendChild(item);
        });
        
        searchResults.classList.add('active');
    }

    // Fetch and display recommendations
    function getRecommendations(playerName) {
        // Show loading state
        loadingIndicator.classList.remove('hidden');
        recommendationsSection.classList.add('hidden');
        errorMessage.classList.add('hidden');
        
        selectedPlayerName.textContent = playerName;

        fetch(`/api/recommend?player=${encodeURIComponent(playerName)}`)
            .then(res => res.json())
            .then(data => {
                loadingIndicator.classList.add('hidden');
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                renderRecommendations(data.recommendations);
                recommendationsSection.classList.remove('hidden');
            })
            .catch(err => {
                loadingIndicator.classList.add('hidden');
                showError('Failed to fetch recommendations. Please try again.');
                console.error(err);
            });
    }

    function renderRecommendations(recs) {
        recommendationsGrid.innerHTML = '';
        
        recs.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'rec-card';
            
            card.innerHTML = `
                <div class="rec-header">
                    <div>
                        <div class="rec-name">${rec.name}</div>
                        <span class="rec-pos">${rec.pos}</span>
                    </div>
                    <div class="rec-similarity">
                        <div class="sim-value">${rec.similarity}%</div>
                        <div class="sim-label">Match</div>
                    </div>
                </div>
                <div class="rec-details">
                    <div class="detail-row">
                        <i class="fa-solid fa-shield-halved"></i>
                        <span>${rec.squad}</span>
                    </div>
                    <div class="detail-row">
                        <i class="fa-solid fa-trophy"></i>
                        <span>${rec.league}</span>
                    </div>
                </div>
            `;
            
            // Allow clicking a recommendation to find similar players to them
            card.addEventListener('click', () => {
                searchInput.value = rec.name;
                window.scrollTo({ top: 0, behavior: 'smooth' });
                getRecommendations(rec.name);
            });
            card.style.cursor = 'pointer';
            
            recommendationsGrid.appendChild(card);
        });
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }
});
