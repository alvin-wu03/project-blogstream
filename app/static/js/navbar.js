function togglePostCreation() {
  const formWrapper = document.querySelector('.new-post-form-wrapper');
  const form = document.querySelector('.new-post-form');

  formWrapper.style.display = (formWrapper.style.display === 'flex') ? 'none' : 'flex';
  if (formWrapper.style.display === 'flex') {
    form.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent scrolling on background content
  } else {
    form.classList.remove('active');
    document.body.style.overflow = ''; // Restore scrolling on background content
  }
}


