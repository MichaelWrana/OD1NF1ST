
import React from "react";

export const status2icon = {
  'error': (<><i className='tim-icons icon-alert-circle-exc text-danger' title='error'></i></>),
  'running': (<><i className='tim-icons icon-spaceship text-warning' title='running'></i></>),
  // 'completed': (<><i className='tim-icons icon-chart-bar-32 text-success' title='completed'></i></>),
  'completed': (<><i className="far fa-check-circle text-success"></i></>),
  'initializing': (<><i className='tim-icons icon-user-run text-info' title='initializing'></i></>),
  'waiting': (<><i className='tim-icons icon-time-alarm text-info' title='waiting'></i></>),
}

export const statusdesp2icon = {
  'failed': (<><i className='tim-icons icon-alert-circle-exc text-danger' title='error'></i></>),
  'completed': (<><i className='tim-icons icon-chart-bar-32 text-success' title='completed'></i></>),
  'submitted': (<><i className='tim-icons icon-user-run text-success' title='initializing'></i></>),
}

export const mission2icon = {
  'pe_elf_analysis': (<><i className='tim-icons icon-cloud-upload-94 text-info' title='pe_elf_analysis'></i></>),
  'pe_elf_indexing': (<><i className='tim-icons icon-chart-pie-36 text-info' title='pe_elf_indexing'></i></>),
}



const blueLineOptions = canvas => {

  let ctx = canvas.getContext("2d");
  let gradientStroke = ctx.createLinearGradient(0, canvas.parentElement.offsetHeight * 1.2, 0, 50);
  gradientStroke.addColorStop(1, "rgba(29,140,248,0.2)");
  gradientStroke.addColorStop(0.4, "rgba(29,140,248,0.0)");
  gradientStroke.addColorStop(0, "rgba(29,140,248,0)"); //blue colors

  return {
    label: "My First dataset",
    fill: true,
    backgroundColor: gradientStroke,
    borderColor: "#1f8ef1",
    borderWidth: 2,
    borderDash: [],
    borderDashOffset: 0.0,
    pointBackgroundColor: "#1f8ef1",
    pointBorderColor: "rgba(255,255,255,0)",
    pointHoverBackgroundColor: "#1f8ef1",
    pointBorderWidth: 20,
    pointHoverRadius: 4,
    pointHoverBorderWidth: 15,
    pointRadius: 4,
  };

}

const greenLineOptions = canvas => {
  let ctx = canvas.getContext("2d");
  let gradientStroke = ctx.createLinearGradient(0, canvas.parentElement.offsetHeight * 1.2, 0, 50);

  gradientStroke.addColorStop(1, "rgba(66,134,121,0.15)");
  gradientStroke.addColorStop(0.4, "rgba(66,134,121,0.0)"); //green colors
  gradientStroke.addColorStop(0, "rgba(66,134,121,0)"); //green colors

  return {
    fill: true,
    backgroundColor: gradientStroke,
    borderColor: "#00d6b4",
    borderWidth: 2,
    borderDash: [],
    borderDashOffset: 0.0,
    pointBackgroundColor: "#00d6b4",
    pointBorderColor: "rgba(255,255,255,0)",
    pointHoverBackgroundColor: "#00d6b4",
    pointBorderWidth: 20,
    pointHoverRadius: 4,
    pointHoverBorderWidth: 15,
    pointRadius: 4,
  };
}

const purpleLineOptions = canvas => {
  let ctx = canvas.getContext("2d");
  let gradientStroke = ctx.createLinearGradient(0, canvas.parentElement.offsetHeight * 1.2, 0, 50);
  gradientStroke.addColorStop(1, "rgba(72,72,176,0.1)");
  gradientStroke.addColorStop(0.4, "rgba(72,72,176,0.0)");
  gradientStroke.addColorStop(0, "rgba(119,52,169,0)"); //purple colors
  return {
    label: "My First dataset",
    fill: true,
    backgroundColor: gradientStroke,
    borderColor: "#d048b6",
    borderWidth: 2,
    borderDash: [],
    borderDashOffset: 0.0,
    pointBackgroundColor: "#d048b6",
    pointBorderColor: "rgba(255,255,255,0)",
    pointHoverBackgroundColor: "#d048b6",
    pointBorderWidth: 20,
    pointHoverRadius: 4,
    pointHoverBorderWidth: 15,
    pointRadius: 4,
  };
}

export const theme2lineColor = { 'blue': blueLineOptions, 'green': greenLineOptions, 'primary': purpleLineOptions }

export const lineChartOptions = {
  maintainAspectRatio: false,
  legend: {
    display: false
  },
  tooltips: {
    backgroundColor: "#f5f5f5",
    titleFontColor: "#333",
    bodyFontColor: "#666",
    bodySpacing: 4,
    xPadding: 12,
    mode: "nearest",
    intersect: 0,
    position: "nearest"
  },
  responsive: true,
  scales: {
    yAxes: [
      {
        ticks: {
          min: 0,
          // max: Math.max.apply(this, values) + 1,
          padding: 20,
          fontColor: "#9a9a9a"
        },
        barPercentage: 1.6,
        gridLines: {
          drawBorder: false,
          color: "rgba(29,140,248,0.0)",
          zeroLineColor: "transparent"
        },
      }
    ],
    xAxes: [
      {
        barPercentage: 1.6,
        gridLines: {
          drawBorder: false,
          color: "rgba(29,140,248,0.1)",
          zeroLineColor: "transparent"
        },
        ticks: {
          padding: 20,
          fontColor: "#9a9a9a"
        }
      }
    ]
  }
}

export const barChartOptions = {
  maintainAspectRatio: false,
  legend: {
    display: false
  },
  tooltips: {
    backgroundColor: "#f5f5f5",
    titleFontColor: "#333",
    bodyFontColor: "#666",
    bodySpacing: 4,
    xPadding: 12,
    mode: "nearest",
    intersect: 0,
    position: "nearest"
  },
  responsive: true,
  scales: {
    yAxes: [
      {
        stacked: true,
        ticks: {
          min: 0,
          // max: Math.max.apply(this, values) + 1,
          padding: 20,
          fontColor: "#9a9a9a"
        },
        gridLines: {
          drawBorder: false,
          color: "rgba(29,140,248,0.0)",
          zeroLineColor: "transparent"
        },
      }
    ],
    xAxes: [
      {
        stacked: true,
        gridLines: {
          drawBorder: false,
          color: "rgba(29,140,248,0.1)",
          zeroLineColor: "transparent"
        },
        ticks: {
          padding: 20,
          fontColor: "#9a9a9a"
        }
      }
    ]
  }
}

export const wrapDataForLineChart = (data, labels, theme) => canvas => {
  var datasets = [];
  if (!Array.isArray(data)) {
    data = [data]
  }
  if (!Array.isArray(labels)) {
    labels = [labels]
  }

  var axes = null;
  var colors = Object.values(theme2lineColor);
  for (let i = 0; i < data.length; i++) {
    axes = data[i].labels;
    var color = colors[i % colors.length]
    if (typeof (theme) !== 'undefined')
      color = theme2lineColor[theme]
    datasets.push({
      ...color(canvas),
      label: labels[i],
      data: data[i].values,
    })
  }

  return {
    labels: axes,
    datasets: datasets
  };

}