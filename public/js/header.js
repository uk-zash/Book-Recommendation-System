document.addEventListener('DOMContentLoaded', function () {
    const burgerMenu = document.querySelector('.burger-menu');
    const navLinks = document.querySelector('.nav-links');
    const container2 = document.querySelector('.container2');

    burgerMenu.addEventListener('click', function () {
      container2.classList.toggle('active');
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 768) {
        container2.classList.remove('active');
      }
    });
    document.addEventListener('click', function (event) {
        if (!container2.contains(event.target) && !burgerMenu.contains(event.target)) {
          container2.classList.remove('active');
        }
      });
  })


  // Function to perform autocomplete
function autocomplete(inputElement, autocompleteResultsElement, bookTitles) {
    const fuse = new Fuse(bookTitles, { shouldSort: true, threshold: 0.3, maxPatternLength: 32, minMatchCharLength: 1, keys: ['name'] });

    inputElement.addEventListener('input', function () {
        const searchValue = this.value.trim();
        const results = fuse.search(searchValue);
        const autocompleteItems = results.slice(0, 5); // Limiting to 5 autocomplete suggestions

        if (searchValue === '') {
            autocompleteResultsElement.innerHTML = '';
            return;
        }

        const autocompleteHTML = autocompleteItems.map(item => `<div class="autocomplete-item">${item.name}</div>`).join('');
        autocompleteResultsElement.innerHTML = autocompleteHTML;

        // Event listener for autocomplete item click
        autocompleteResultsElement.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => {
                inputElement.value = item.innerText;
                autocompleteResultsElement.innerHTML = ''; // Clear autocomplete results
            });
        });
    });
}

// Fetch book titles from the server and perform autocomplete
window.addEventListener('DOMContentLoaded', () => {
    const inputElement = document.getElementById('bookNameInput');
    const autocompleteResultsElement = document.getElementById('autocompleteResults');

    // Fetch book titles from the server or use a preloaded list
    const bookTitles = ["Title 1", "Title 2", "Title 3"]; // Replace with your actual book titles

    // Perform autocomplete
    autocomplete(inputElement, autocompleteResultsElement, bookTitles);
});
