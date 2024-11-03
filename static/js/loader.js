// Show loader before navigating away
window.addEventListener('beforeunload', function () {
    document.getElementById('loader').style.display = 'flex';
});

// Hide loader on load and pageshow
function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

window.addEventListener('load', hideLoader);
window.addEventListener('pageshow', hideLoader);
