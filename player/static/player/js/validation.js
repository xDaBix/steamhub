document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('registrationForm').addEventListener('submit', function(event) {
        event.preventDefault(); 

        const email = document.getElementById('id_email').value;
        const username = document.getElementById('id_username').value;
        const password = document.getElementById('id_password').value;
        const gender = document.getElementById('id_gender').value;
        const firstname = document.getElementById('id_firstname').value;
        const lastname = document.getElementById('id_lastname').value;
        const contactno = document.getElementById('id_contactno').value;

        let valid = true;
        let errorMessages = [];

        
        if (!username || !email || !password || !gender || !firstname || !lastname || !contactno) {
            errorMessages.push('Please fill out all fields.');
            valid = false;
        }

        
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            errorMessages.push('Please enter a valid email address.');
            valid = false;
        }

        
        if (password.length < 8) {
            errorMessages.push('Password must be at least 8 characters long.');
            valid = false;
        }

        const passwordPattern = /^(?=.*[a-zA-Z])(?=.*\d).+$/;
        if (!passwordPattern.test(password)) {
            errorMessages.push('Password must contain both letters and numbers.');
            valid = false;
        }

        
        const namePattern = /^[a-zA-Z]+$/;
        if (!namePattern.test(firstname)) {
            errorMessages.push('First name must contain only letters.');
            valid = false;
        }

        if (!namePattern.test(lastname)) {
            errorMessages.push('Last name must contain only letters.');
            valid = false;
        }

        
        const contactnoPattern = /^[6789]\d{9}$/;
        if (!contactnoPattern.test(contactno)) {
            errorMessages.push('Contact number must start with 6, 7, 8, or 9 and be 10 digits long.');
            valid = false;
        }

        
        if (!valid) {
            alert(errorMessages.join('\n'));
            return;
        }


        fetch(`/check-user/?email=${encodeURIComponent(email)}&username=${encodeURIComponent(username)}`)
            .then(response => response.json())
            .then(data => {
                if (data.email_exists) {
                    errorMessages.push('Email is already registered.');
                }
                if (data.username_exists) {
                    errorMessages.push('Username is already taken.');
                }

                
                if (errorMessages.length > 0) {
                    alert(errorMessages.join('\n'));
                } else {

                    event.target.submit();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while validating the form. Please try again.');
            });
    });
});
