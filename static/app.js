const ratingForm = document.getElementById('rating-form');
const submitButton = document.getElementById('submit-rating');
const reaction = document.getElementById('reaction');

ratingForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const selected = ratingForm.querySelector('input[name="rating"]:checked');
  if (!selected) return;

  submitButton.disabled = true;
  submitButton.textContent = 'Saving...';

  try {
    const response = await fetch('/api/rate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating: Number(selected.value) })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Could not save rating.');

    reaction.textContent = result.message;
    ratingForm.reset();
  } catch (error) {
    reaction.textContent = error.message || 'Please try again.';
  } finally {
    reaction.hidden = false;
    submitButton.disabled = false;
    submitButton.textContent = 'Submit Rating';
  }
});
