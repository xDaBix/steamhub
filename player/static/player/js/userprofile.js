
document.addEventListener('DOMContentLoaded', function() {
  // Validation for Edit Profile Form
  document.querySelector('.edit-profile-form-wrap form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission

    const firstName = document.getElementById('first-name').value.trim();
    const lastName = document.getElementById('last-name').value.trim();
    const contactNo = document.getElementById('contact-no').value.trim();
    const dob = document.getElementById('dob').value.trim();

    let valid = true;
    let errorMessages = [];

    // Check required fields
    if (!firstName || !lastName  || !contactNo || !dob) {
      errorMessages.push('Please fill out all fields.');
      valid = false;
    }

    
    const contactNoPattern = /^[6789]\d{9}$/;
    if (!contactNoPattern.test(contactNo)) {
      errorMessages.push('Contact Number must start with 6, 7, 8, or 9 and be 10 digits long.');
      valid = false;
    }

    if (!valid) {
      alert(errorMessages.join('\n'));
      return;
    }

    
  });


  document.querySelector('.change-password-form-wrap form').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const currentPassword = document.getElementById('current-password').value.trim();
    const newPassword = document.getElementById('new-password').value.trim();
    const confirmPassword = document.getElementById('confirm-password').value.trim();

    let valid = true;
    let errorMessages = [];


    if (!currentPassword) {
      valid = false;
      errorMessages.push('Current Password cannot be empty.');
    }


    if (!newPassword) {
      valid = false;
      errorMessages.push('New Password cannot be empty.');
    }

    
    if (!confirmPassword) {
      valid = false;
      errorMessages.push('Confirm Password cannot be empty.');
    }

    
    if (newPassword !== confirmPassword) {
      valid = false;
      errorMessages.push('New Password and Confirm Password do not match.');
    }

    if (!valid) {
      alert(errorMessages.join('\n'));
      return;
    }

    event.target.submit(); 
  });
});
