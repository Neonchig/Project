const socket = new WebSocket("ws://localhost:9801/")

socket.addEventListener("open", (event) => {
  console.log("Connection opened");
  socket.send('{"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlNTcxYjNjYi0yOTcyLTQ4MzgtYjdmNS1hNDQwMmVhY2Y2YTMiLCJzdWIiOiJuZW9uaWNoZSIsImF1ZCI6InVzZXIiLCJpYXQiOjE3OTA1MTA0MzMuMTgxOTY1LCJleHAiOjE3OTA1MTEzMzMuMTgxOTcxfQ.l7KWVLskPd_Ez0Z4xHPZMian8lASqIiyi39CAulF64g"}');
});

socket.addEventListener("message", (event) => {
  console.log("message from server: ", event.data);
})

socket.addEventListener("error", (event) => {
  console.log("server error: ", event.data)
});


const toggle = document.getElementById('menuToggle');
const closeBtn = document.getElementById('menuClose');
const menu = document.getElementById('sideMenu');
const overlay = document.getElementById('menuOverlay');

function openMenu(){
  menu.classList.add('open');
  overlay.classList.add('open');
  menu.setAttribute('aria-hidden', 'false');
  toggle.setAttribute('aria-expanded', 'true');
}
function closeMenu(){
  menu.classList.remove('open');
  overlay.classList.remove('open');
  menu.setAttribute('aria-hidden', 'true');
  toggle.setAttribute('aria-expanded', 'false');
}

toggle.addEventListener('click', openMenu);
closeBtn.addEventListener('click', closeMenu);
overlay.addEventListener('click', closeMenu);
document.addEventListener('keydown', (e) => {
  if(e.key === 'Escape') closeMenu();
});
