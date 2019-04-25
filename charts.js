// Bar chart
var results_chart = new Chart(document.getElementById("bar-chart"), {
    type: 'bar',
    data: {
      labels: ["Information Sharing","Shared Understanding","Other"],
      datasets: [
        {
          label: "Fraction (%)",
          backgroundColor: ["#3e95cd", "#3e95cd", "#3e95cd"],
          data: [0,0,0]
        }
      ]
    },
    options: {
      legend: { display: false },
      scales: {
          yAxes: [{
              ticks: {
                  fontSize: 40,
                  suggestedMin: 0,
                  suggestedMax: 100
              }
          }]
      }
    }
});