
import React from "react";
import * as chartjs from "react-chartjs-2";
import {
    Card,
    CardHeader,
    CardBody,
    Row,
    Col
} from "reactstrap";

export class Bar extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            mission_id: props.mission_id
        }
        console.log(this.props.data)
    }

    data = canvas => {
        let ctx = canvas.getContext("2d");

        let gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

        gradientStroke.addColorStop(1, "rgba(72,72,176,0.1)");
        gradientStroke.addColorStop(0.4, "rgba(72,72,176,0.0)");
        gradientStroke.addColorStop(0, "rgba(119,52,169,0)"); //purple colors

        var datasets = [];
        var axes = []
        for (let key in this.props.data) {
            let res = this.props.data[key];
            axes = res.x;
            datasets.push({
                labels: res.x,
                label: key,
                fill: true,
                backgroundColor: gradientStroke,
                hoverBackgroundColor: gradientStroke,
                borderColor: "#d048b6",
                borderWidth: 2,
                borderDash: [],
                borderDashOffset: 0.0,
                data: res.y
            });
        }


        return { datasets: datasets, labels: axes };
    }

    options = {
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
                    gridLines: {
                        drawBorder: false,
                        color: "rgba(225,78,202,0.1)",
                        zeroLineColor: "transparent"
                    },
                    ticks: {
                        suggestedMin: 0,
                        suggestedMax: 6,
                        padding: 20,
                        fontColor: "#9e9e9e"
                    }
                }
            ],
            xAxes: [
                {
                    gridLines: {
                        drawBorder: false,
                        color: "rgba(225,78,202,0.1)",
                        zeroLineColor: "transparent"
                    },
                    ticks: {
                        padding: 20,
                        fontColor: "#9e9e9e"
                    }
                }
            ]
        }
    }

    render() {
        return (
            <>
                <Card className={"card-chart " + this.props.className}>
                    <CardHeader>
                        {
                            this.props.name.split('-').map((vs, k) => (
                                <h5 className="card-category" key={k}>{vs}</h5>))
                        }
                    </CardHeader>
                    <CardBody>
                        <Row>
                            <Col md="12">
                                <div className='chart-js-container-sm' ref="chart">
                                    {!this.props.vertical ?
                                        <chartjs.HorizontalBar data={this.data} options={this.options}>
                                        </chartjs.HorizontalBar> :
                                        <chartjs.Bar data={this.data} options={this.options}>
                                        </chartjs.Bar>
                                    }
                                </div>
                            </Col>
                        </Row>
                    </CardBody>
                </Card>
            </>)
    }
}


export default Bar