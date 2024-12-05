const togglebtn = document.querySelector('.toggle-btn');
const sidebar= document.querySelector('.sidebar');
const togglclose = document.querySelector('.toggle-close');
togglebtn.onclick = function() {
    sidebar.classList.toggle('open');
    togglebtn.classList.toggle('hide');
    const isOpen = sidebar.classList.contains('open');

    sidebar.classList = isOpen
    ? 'toggle-btn open text-black bg-white/30 backdrop-blur-sm right-0 top-0 fixed w-80 h-screen shadow-2xl shadow-white z-50'
    : 'toggle-btn hidden';
}
togglclose.onclick = function() {
    sidebar.classList.toggle('close');
    const isClose = sidebar.classList.contains('close');

    sidebar.classList = isClose
    ? 'toggle-close hidden'
    : 'toggle-close open text-black bg-white/30 backdrop-blur-sm right-0 top-0 fixed w-80 h-screen shadow-2xl shadow-white z-50';
}
