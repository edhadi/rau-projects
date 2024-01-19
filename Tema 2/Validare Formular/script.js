function validateForm(event) {
    event.preventDefault();
    // Reset Elements
    document.getElementById('emailError').textContent = '';
    document.getElementById('passwordError').textContent = '';
    document.getElementById('repeatPasswordError').textContent = '';

    document.getElementById('email').style.borderColor = '';
    document.getElementById('password').style.borderColor = '';
    document.getElementById('repeatPassword').style.borderColor = '';

    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    var repeatPassword = document.getElementById('repeatPassword').value;

    // Email Validation
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email.trim() === '' || !emailRegex.test(email)) {
        document.getElementById('emailError').textContent = 'Invalid email address';
        document.getElementById('email').style.borderColor = 'red';
        return false;
    }


    // Password Validation
    if (password.length < 8) {
        document.getElementById('passwordError').textContent = 'Password must be at least 8 characters';
        document.getElementById('password').style.borderColor = 'red';
        return false;
    }

    // Password Confirmation Validation
    if (password !== repeatPassword) {
        document.getElementById('repeatPasswordError').textContent = 'Passwords do not match';
        document.getElementById('repeatPassword').style.borderColor = 'red';
        return false;
    }

    if (email.trim() === '') {
        document.getElementById('emailError').textContent = 'Email is required';
        document.getElementById('email').style.borderColor = 'red';
        return false;
    }

    if (password === '') {
        document.getElementById('passwordError').textContent = 'Password is required';
        document.getElementById('password').style.borderColor = 'red';
        return false;
    }

    if (repeatPassword === '') {
        document.getElementById('repeatPasswordError').textContent = 'Repeat Password is required';
        document.getElementById('repeatPassword').style.borderColor = 'red';
        return false;
    }

    // If validation pass, turn border to GREEN
    document.getElementById('email').style.borderColor = 'green';
    document.getElementById('password').style.borderColor = 'green';
    document.getElementById('repeatPassword').style.borderColor = 'green';
    console.log('Form submitted successfully!');

}

document.querySelector('form').addEventListener('submit', validateForm);