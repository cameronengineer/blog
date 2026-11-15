// Keep the contents available without making phone readers scroll past it.
if (window.matchMedia('(max-width: 850px)').matches) {
  document.querySelectorAll('.contents').forEach(contents => { contents.open = false; });
}

const search = document.querySelector('[data-search]');
if (search) {
  search.hidden = false;
  const input = search.querySelector('input');
  const notes = [...document.querySelectorAll('[data-note]')];
  const status = document.querySelector('[data-search-status]');
  input.addEventListener('input', () => {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const note of notes) {
      note.hidden = !note.textContent.toLocaleLowerCase().includes(query);
      if (!note.hidden) count++;
    }
    status.textContent = count ? `${count} ${count === 1 ? 'note' : 'notes'}` : 'No notes found. Try another word or topic.';
  });
}
