function formatdate() {
  moment.defaultFormat = "YYYY/MM/DD hh:mm A";
  for (let elem of document.getElementsByClassName("timespec")) {
    elem.innerText = moment.utc(elem.innerText).local().format()
  };
}

window.addEventListener("DOMContentLoaded", formatdate);
