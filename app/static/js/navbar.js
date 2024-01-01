function togglePostCreation(event) {
  event.preventDefault();
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

function togglePostEdit(event) {
  event.preventDefault();
  const formWrapper = document.querySelector('.edit-post-form-wrapper');
  const form = document.querySelector('.edit-post-form');

  formWrapper.style.display = (formWrapper.style.display === 'flex') ? 'none' : 'flex';
  if (formWrapper.style.display === 'flex') {
    form.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent scrolling on background content
  } else {
    form.classList.remove('active');
    document.body.style.overflow = ''; // Restore scrolling on background content
  }
}

function togglePostComment(event) {
  event.preventDefault();
  const formWrapper = document.querySelector('.comment-post-form-wrapper');
  const form = document.querySelector('.comment-post-form');

  formWrapper.style.display = (formWrapper.style.display === 'block') ? 'none' : 'block';
  if (formWrapper.style.display === 'block') {
    form.classList.add('active');
  } else {
    form.classList.remove('active');
  }
}