
import React from "react";
import * as chartjs from "react-chartjs-2";
import {
    Card,
    CardHeader,
    CardBody,
    Row,
    Col
} from "reactstrap";

import { lineChartOptions, theme2lineColor, wrapDataForLineChart, status2icon, mission2icon } from '../../variables/charts.jsx'


export class Line extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            mission_id: props.mission_id,
            theme: props.theme || 'blue'
        }
    }

    data = canvas => {
        let ctx = canvas.getContext("2d");

        let gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);

        gradientStroke.addColorStop(1, "rgba(72,72,176,0.1)");
        gradientStroke.addColorStop(0.4, "rgba(72,72,176,0.0)");
        gradientStroke.addColorStop(0, "rgba(119,52,169,0)"); //purple colors

        var datasets = [];
        var axes = []
        var color = theme2lineColor[this.state.theme]
        for (let key in this.props.data) {
            let res = this.props.data[key];
            axes = res.x;
            datasets.push({
                ...color(canvas),
                label: key,
                data: res.y
            });
        }


        return { datasets: datasets, labels: axes };
    }

    render() {
        return (
            <>
                <Card className={this.props.className + "card-chart"}>
                    <CardHeader>
                        {
                            <h5 className="card-category">{this.props.name}</h5>
                        }
                    </CardHeader>
                    <CardBody>
                        <Row>
                            <Col md="12">
                                <div className='chart-js-container-sm' ref="chart">
                                    <chartjs.Line data={this.data}
                                        options={lineChartOptions}
                                    />
                                </div>
                            </Col>
                        </Row>
                    </CardBody>
                </Card>
            </>)
    }
}


export default Line