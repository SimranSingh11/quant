function showNotifications() {
  var x = document.getElementById('notification__content');
  if ( window.getComputedStyle(x, null).getPropertyValue("display") === 'none') {
      x.style.display = 'block';
  } else {
      x.style.display = 'none';
  }
}
