function repairDone(repairId) {
  fetch("/repair_done", {
    method: "POST",
    body: JSON.stringify({ repairId: repairId }),
  }).then((_res) => {
    window.location.href = "/repair";
  });
}


function repairShow(repairId) {
  fetch("/parts", {
    method: "POST",
    body: JSON.stringify({ repairId: repairId }),
  }).then((_res) => {
    window.location.href = "/parts";
  });
}