// ========== UNIVERSAL SEARCHABLE SELECT ========== //
// Keep track of currently open dropdown
let currentlyOpenDropdown = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize searchable selects
    initSearchableSelects();
    
    // Re-initialize when new content is added dynamically
    const observer = new MutationObserver(function(mutations) {
        let shouldReinit = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                shouldReinit = true;
            }
        });
        if (shouldReinit) {
            setTimeout(initSearchableSelects, 100); // Small delay to ensure DOM is ready
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

function initSearchableSelects() {
    // First handle data-enhanced selects (explicit opt-in)
    const forcedSelects = document.querySelectorAll('select[data-enhanced]:not(.searchable-converted)');
    forcedSelects.forEach(function(select) {
        makeSearchable(select);
    });
    
    // Then handle regular selects (5+ options, not already handled, not explicitly excluded)
    const regularSelects = document.querySelectorAll('select:not(.no-search):not(.searchable-converted):not([data-enhanced])');
    regularSelects.forEach(function(select) {
        const options = select.querySelectorAll('option[value]:not([value=""])');
        if (options.length >= 5) {
            makeSearchable(select);
        }
    });
}

function makeSearchable(selectElement) {
    // Skip if already converted
    if (selectElement.classList.contains('searchable-converted')) return;
    
    const container = document.createElement('div');
    container.className = 'searchable-select-container';
    
    // Insert container before select and move select inside
    selectElement.parentNode.insertBefore(container, selectElement);
    container.appendChild(selectElement);
    
    // Create dropdown structure
    const dropdown = document.createElement('div');
    dropdown.className = 'searchable-select-dropdown';
    dropdown.innerHTML = `
        <div class="searchable-select-search-wrapper">
            <input type="text" class="searchable-select-search" placeholder="Type to search...">
        </div>
        <div class="searchable-select-options"></div>
    `;
    
    container.appendChild(dropdown);
    
    const searchInput = dropdown.querySelector('.searchable-select-search');
    const optionsContainer = dropdown.querySelector('.searchable-select-options');
    
    // Hide original select but keep it functional
    selectElement.classList.add('searchable-converted');
    selectElement.tabIndex = -1; // Remove from tab order
    
    // Populate options
    function populateOptions(searchTerm = '') {
        optionsContainer.innerHTML = '';
        const selectOptions = selectElement.querySelectorAll('option');
        
        selectOptions.forEach(option => {
            // Skip empty placeholder options unless they have meaningful text
            if (option.value === '' && option.textContent.trim() === '') return;
            if (option.value === '' && option.textContent.trim() === '---------') return;
            
            const text = option.textContent.toLowerCase();
            const search = searchTerm.toLowerCase();
            
            // Show all if no search term, otherwise filter
            if (searchTerm === '' || text.includes(search)) {
                const optionDiv = document.createElement('div');
                optionDiv.className = 'searchable-select-option';
                
                // Highlight matching text
                if (searchTerm !== '') {
                    const escapedSearch = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                    const regex = new RegExp(`(${escapedSearch})`, 'gi');
                    optionDiv.innerHTML = option.textContent.replace(regex, '<span class="searchable-highlight">$1</span>');
                } else {
                    optionDiv.textContent = option.textContent;
                }
                
                optionDiv.dataset.value = option.value;
                
                // Mark selected option
                if (option.selected) {
                    optionDiv.classList.add('selected');
                }
                
                optionDiv.addEventListener('click', function() {
                    // Update original select
                    selectElement.value = option.value;
                    
                    // Trigger change event for any listeners
                    selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Update selected class
                    optionsContainer.querySelectorAll('.searchable-select-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    this.classList.add('selected');
                    
                    // Hide dropdown
                    hideDropdown(dropdown);
                });
                
                optionsContainer.appendChild(optionDiv);
            }
        });
    }
    
    // Show dropdown and focus search
    selectElement.addEventListener('focus', function(e) {
        e.stopPropagation();
        showDropdown();
    });
    
    // Also show dropdown when clicking the container
    selectElement.addEventListener('click', function(e) {
        e.stopPropagation();
        showDropdown();
    });
    
    function showDropdown() {
        // Close any currently open dropdown
        if (currentlyOpenDropdown && currentlyOpenDropdown !== dropdown) {
            hideDropdown(currentlyOpenDropdown);
        }
        
        // Position dropdown properly before showing
        positionDropdown();
        
        dropdown.style.display = 'block';
        currentlyOpenDropdown = dropdown;
        searchInput.focus();
        searchInput.value = '';
        populateOptions();
    }
    
    function positionDropdown() {
        // Reset positioning
        dropdown.style.top = '';
        dropdown.style.bottom = '';
        dropdown.style.marginTop = '';
        dropdown.style.marginBottom = '';
        
        // Get element positions
        const rect = selectElement.getBoundingClientRect();
        const dropdownRect = dropdown.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // Calculate available space
        const spaceBelow = viewportHeight - rect.bottom;
        const spaceAbove = rect.top;
        const dropdownHeight = Math.min(250, dropdownRect.height || 250);
        
        // Position based on available space
        if (spaceBelow >= dropdownHeight || spaceBelow >= spaceAbove) {
            // Position below
            dropdown.style.top = '100%';
            dropdown.style.bottom = 'auto';
            dropdown.style.marginTop = '2px';
            dropdown.style.marginBottom = '0';
        } else {
            // Position above
            dropdown.style.top = 'auto';
            dropdown.style.bottom = '100%';
            dropdown.style.marginTop = '0';
            dropdown.style.marginBottom = '2px';
        }
        
        // Ensure dropdown doesn't go off screen horizontally
        const containerRect = container.getBoundingClientRect();
        if (containerRect.right > viewportWidth) {
            dropdown.style.left = 'auto';
            dropdown.style.right = '0';
        } else {
            dropdown.style.left = '0';
            dropdown.style.right = 'auto';
        }
    }
    
    function hideDropdown(dropdownToHide) {
        if (dropdownToHide) {
            dropdownToHide.style.display = 'none';
            searchInput.value = '';
            if (currentlyOpenDropdown === dropdownToHide) {
                currentlyOpenDropdown = null;
            }
        }
    }
    
    // Search functionality
    searchInput.addEventListener('input', function() {
        populateOptions(this.value);
    });
    
    // Keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        const options = optionsContainer.querySelectorAll('.searchable-select-option');
        if (options.length === 0) return;
        
        let selected = optionsContainer.querySelector('.searchable-select-option.selected');
        let currentIndex = selected ? Array.from(options).indexOf(selected) : -1;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, options.length - 1);
                updateSelection(options, currentIndex);
                break;
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, 0);
                updateSelection(options, currentIndex);
                break;
            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0 && currentIndex < options.length) {
                    options[currentIndex].click();
                }
                break;
            case 'Escape':
                hideDropdown(dropdown);
                break;
        }
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!container.contains(e.target)) {
            hideDropdown(dropdown);
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (currentlyOpenDropdown === dropdown && dropdown.style.display === 'block') {
            positionDropdown();
        }
    });
    
    // Handle select changes from external sources
    selectElement.addEventListener('change', function() {
        setTimeout(() => {
            populateOptions();
        }, 50);
    });
    
    // Initial population
    populateOptions();
    
    function updateSelection(options, index) {
        options.forEach((option, i) => {
            if (i === index) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }
}

// Utility function to manually initialize searchable selects
function makeSelectSearchable(selector) {
    const elements = document.querySelectorAll(selector);
    elements.forEach(makeSearchable);
}

// Export for global use
window.makeSelectSearchable = makeSelectSearchable;