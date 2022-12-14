//
// Scripts
// 
// Bootstrap JS scripts for navbar animation/ shrink

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink');
        } else {
            navbarCollapsible.classList.add('navbar-shrink');
        }
    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
    }

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });


    // Stripe payments script JS taken from TestDriven.io
    // Get stripe public key
    fetch("/payments/config/")
    .then((result) => { return result.json(); })
    .then((data) => {
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);

    // Event handler
    document.querySelector("#confirmBtn").addEventListener("click", () => {
        // Get Checkout Session ID
        // Pass in the pk from the URL
        fetch("/payments/create-checkout-session/?pk={{ request.GET.pk }}")
        .then((result) => { return result.json(); })
        .then((data) => {
            // If route passed error, throw an Error. 
            if (data.error) {
              throw Error(data.error);
          } else {
            // Redirect to Stripe Checkout
            return stripe.redirectToCheckout({sessionId: data.sessionId});
          }
        })
        .then((res) => {
        console.log(res);
        });
    });
});

});
