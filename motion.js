/* Native dialogs retain focus management while local CSS animates states. */
const modalTimers=new WeakMap();
const reduceMotion=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
function openDialog(dialog){
 clearTimeout(modalTimers.get(dialog));dialog.classList.remove('is-closing');
 if(!dialog.open)dialog.showModal();
 void dialog.offsetWidth;dialog.classList.add('is-open');
}
function closeDialog(dialog){
 if(!dialog.open)return;
 clearTimeout(modalTimers.get(dialog));dialog.classList.remove('is-open');dialog.classList.add('is-closing');
 const closeMs=reduceMotion()?0:parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--modal-close-dur'))||150;
 modalTimers.set(dialog,setTimeout(()=>{dialog.close();dialog.classList.remove('is-closing')},closeMs));
}
function revealDetail(panel,key){
 if(panel.dataset.key===key)return;
 panel.dataset.key=key;panel.style.transition='none';panel.dataset.open='false';
 void panel.offsetWidth;panel.style.transition='';panel.dataset.open='true';
}
for(const acc of document.querySelectorAll('.t-acc')){
 const head=acc.querySelector('.t-acc-head'),panel=acc.querySelector('.t-acc-panel');
 head.addEventListener('click',()=>{const open=acc.dataset.open!=='true';acc.dataset.open=String(open);head.setAttribute('aria-expanded',String(open));panel.inert=!open;panel.setAttribute('aria-hidden',String(!open))});
}
