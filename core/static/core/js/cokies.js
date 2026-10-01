document.addEventListener('DOMContentLoaded', function() {

    const cookieBanner = document.getElementById('cookie-banner');
    const cookieAccept = document.getElementById('cookie-accept');

    // Verificamos se o banner e o botão existem
    if (!cookieBanner || !cookieAccept) {
        return;
    }

    const ACCEPT_DURATION_DAYS = 180;

   
    let acceptedAt = null;
    try {
        acceptedAt = localStorage.getItem('cookieAcceptedAt');
    } catch (e) {
        console.warn('localStorage indisponível:', e);
    }

    
    const isValid = acceptedAt &&
        (Date.now() - Number(acceptedAt)) < ACCEPT_DURATION_DAYS * 86400000;

    if (isValid) {
        cookieBanner.style.display = 'none';
        return;
    }

    cookieAccept.addEventListener('click', function() {
        try {
            localStorage.setItem('cookieAcceptedAt', Date.now().toString());
        } catch (e) {
            console.warn('Não foi possível salvar a preferência de cookies:', e);
        }

        cookieBanner.style.display = 'none';
    });

});