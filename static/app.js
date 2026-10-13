// Bootstrap form validation
document.querySelectorAll('.needs-validation').forEach(form => {
  form.addEventListener('submit', e => {
    if (!form.checkValidity()) { e.preventDefault(); e.stopPropagation(); }
    form.classList.add('was-validated');
  });
});

// Contact donor: phone stays masked until the person confirms
const modalEl = document.getElementById('contactModal');
const modal = new bootstrap.Modal(modalEl);
const foot = document.getElementById('cmFoot');

document.querySelectorAll('.contact-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.getElementById('cmTitle').textContent = 'Contact ' + btn.dataset.name;
    document.getElementById('cmPhone').textContent = btn.dataset.mask;
    foot.innerHTML = '<button class="btn btn-rs" id="reveal">I need blood, show contact</button>' +
                     '<button class="btn btn-outline-light" data-bs-dismiss="modal">Close</button>';
    document.getElementById('reveal').addEventListener('click', async () => {
      try {
        const res = await fetch('/contact/' + btn.dataset.id, { method: 'POST' });
        if (!res.ok) throw new Error();
        const data = await res.json();
        document.getElementById('cmPhone').textContent = data.phone;
        foot.innerHTML = '<a class="btn btn-rs" href="tel:' + data.phone + '">Call</a>' +
          '<a class="btn btn-outline-light" target="_blank" rel="noopener" href="' + data.whatsapp + '">WhatsApp</a>' +
          '<button class="btn btn-outline-secondary" data-bs-dismiss="modal">Close</button>';
      } catch (err) {
        document.getElementById('cmPhone').textContent = 'Could not load. Try again.';
      }
    });
    modal.show();
  });
});
