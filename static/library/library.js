document.addEventListener('DOMContentLoaded', function(){
  // Tabs
  const tabs = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.tab-content');
  tabs.forEach(btn=>btn.addEventListener('click', ()=>{
    tabs.forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    const target = btn.dataset.tab;
    contents.forEach(c=>{ if(c.id===target) c.classList.remove('hidden'); else c.classList.add('hidden'); });
  }));

  // Modal helpers
  const csrf = document.querySelector('meta[name="csrf-token"]') ? document.querySelector('meta[name="csrf-token"]').getAttribute('content') : '';
  const createCard = document.getElementById('create-list-card');
  const createModal = document.getElementById('createListModal');
  const listDetailModal = document.getElementById('listDetailModal');

  function openModal(modal){ if(!modal) return; modal.classList.remove('hidden'); }
  function closeModal(modal){ if(!modal) return; modal.classList.add('hidden'); }

  // open create list modal
  if(createCard){ createCard.addEventListener('click', ()=> openModal(createModal)); }
  // modal close/cancel
  document.querySelectorAll('.modal-close, #create-list-cancel').forEach(el=> el && el.addEventListener('click', (e)=>{ e.preventDefault(); closeModal(createModal); closeModal(listDetailModal); }));

  // emoji selection
  let selectedEmoji = '';
  document.querySelectorAll('.emoji-option').forEach(btn=> btn.addEventListener('click', ()=>{
    document.querySelectorAll('.emoji-option').forEach(b=>b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedEmoji = btn.textContent.trim();
  }));

  // create list action
  const createConfirm = document.getElementById('create-list-confirm');
  if(createConfirm){
    createConfirm.addEventListener('click', async ()=>{
      const name = document.getElementById('new-list-name').value.trim();
      if(!name) { alert('Lütfen bir isim girin.'); return; }
      try{
        const form = new FormData();
        form.append('name', name);
        form.append('emoji', selectedEmoji || '');
        const res = await fetch('/accounts/library/create-list/', { method: 'POST', body: form, headers: { 'X-CSRFToken': csrf } });
        const data = await res.json();
        if(data.ok){
          // append new list card to grid
          const grid = document.querySelector('.custom-lists-grid');
          if(grid){
            const div = document.createElement('div');
            div.className = 'card library-card custom-list-card';
            div.dataset.listId = data.id;
            div.innerHTML = `<div class="poster"><div class="poster-fallback large-emoji">${data.emoji||''}</div></div><div class="title">${data.name}</div><div class="year"></div>`;
            grid.appendChild(div);
          }
          // reset and close
          document.getElementById('new-list-name').value = '';
          selectedEmoji = '';
          closeModal(createModal);
        } else {
          alert('Oluşturulamadı: ' + (data.error||''));
        }
      }catch(err){ console.error(err); alert('Sunucu hatası'); }
    });
  }

  // Open list detail modal when clicking a custom-list-card
  document.addEventListener('click', function(e){
    const cl = e.target.closest('.custom-list-card');
    if(cl){
      const listId = cl.dataset.listId;
      // For now, show empty modal with title from card
      const title = cl.querySelector('.title') ? cl.querySelector('.title').textContent : 'Liste';
      document.getElementById('list-detail-title').textContent = title;
      // TODO: fetch list items via API when available; for now leave grid empty
      openModal(listDetailModal);
    }
  });

  // Delete overlay handling: delegate
  document.addEventListener('click', async function(e){
    if(e.target.closest('.btn-delete')){
      const btn = e.target.closest('.btn-delete');
      const card = btn.closest('.card');
      if(!card) return;
      if(!confirm('Bu öğeyi silmek istediğinize emin misiniz?')) return;
      // attempt to delete: prefer custom-list-item endpoint if inside list modal (not implemented); fallback to library delete
      const itemPk = card.dataset.itemPk;
      try{
        const form = new FormData();
        if(itemPk) form.append('item_pk', itemPk);
        // call library delete endpoint
        const res = await fetch('/accounts/library/delete-item/', { method: 'POST', body: form, headers: { 'X-CSRFToken': csrf } });
        const data = await res.json();
        if(data.ok){
          card.remove();
        } else {
          alert('Silme hatası: ' + (data.error||''));
        }
      }catch(err){ console.error(err); alert('Silme sırasında hata oluştu'); }
    }
  });

});
