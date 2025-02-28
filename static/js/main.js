// Main JavaScript file for the Dinner Planner application

// Enable tooltips everywhere
document.addEventListener('DOMContentLoaded', function() {
    // This is where we'll initialize any JavaScript libraries or components
    console.log('Dinner Planner application initialized');
    
    // Example function for future use
    window.formatDate = function(dateString) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    };
}); 
