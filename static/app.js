const toast = document.getElementById('toast');
const listEl = document.getElementById('bubble-list');
const emptyEl = document.getElementById('empty');
const createForm = document.getElementById('create-form');
const refreshBtn = document.getElementById('refresh');
const template = document.getElementById('bubble-template');

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}

function renderResources(container, resources) {
  container.innerHTML = '';
  if (!resources || resources.length === 0) {
    container.innerHTML = '<p class="empty">暂无资料，尝试检索一个关键词。</p>';
    return;
  }
  resources.forEach((res) => {
    const item = document.createElement('div');
    item.className = 'resource';
    item.innerHTML = `
      <h4>${res.title || '无标题'}</h4>
      <p>${res.snippet || ''}</p>
      ${res.url ? `<a href="${res.url}" target="_blank" rel="noopener">${res.url}</a>` : ''}
    `;
    container.appendChild(item);
  });
}

function renderBubbles(data) {
  listEl.innerHTML = '';
  const bubbles = data.bubbles || [];
  emptyEl.style.display = bubbles.length ? 'none' : 'block';
  bubbles.forEach((bubble) => {
    const card = template.content.cloneNode(true);
    card.querySelector('.bubble-id').textContent = `Bubble #${bubble.id}`;
    card.querySelector('.bubble-title').textContent = bubble.title;
    card.querySelector('.bubble-date').textContent = new Date(bubble.created_at).toLocaleString();
    card.querySelector('.bubble-idea').textContent = bubble.idea;

    const resourcesEl = card.querySelector('.resources');
    renderResources(resourcesEl, bubble.resources);

    const fetchForm = card.querySelector('.fetch-form');
    fetchForm.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const query = fetchForm.querySelector('input[name="query"]').value.trim();
      if (!query) return;
      fetchForm.querySelector('button').disabled = true;
      try {
        const res = await fetch(`/api/bubbles/${bubble.id}/fetch`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query }),
        });
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.error || '请求失败');
        renderResources(resourcesEl, payload.bubble.resources);
        showToast('资料已更新');
      } catch (err) {
        showToast(err.message || '请求失败');
      } finally {
        fetchForm.querySelector('button').disabled = false;
      }
    });

    listEl.appendChild(card);
  });
}

async function fetchBubbles() {
  try {
    const res = await fetch('/api/bubbles');
    const data = await res.json();
    renderBubbles(data);
  } catch (err) {
    showToast('加载失败，请稍后重试');
  }
}

createForm.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const form = new FormData(createForm);
  const payload = Object.fromEntries(form.entries());
  try {
    const res = await fetch('/api/bubbles', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '创建失败');
    createForm.reset();
    showToast('Bubble 创建成功');
    fetchBubbles();
  } catch (err) {
    showToast(err.message || '创建失败');
  }
});

refreshBtn.addEventListener('click', fetchBubbles);

fetchBubbles();
