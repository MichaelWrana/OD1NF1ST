import React from "react";
import * as d3 from "d3"
import {
    Card,
    CardHeader,
    CardBody,
    Row, Button, CardDeck,
    Col, Modal, ModalHeader, ModalBody, ModalFooter
} from "reactstrap";

import { get_resource } from "../../variables/api"
/* eslint-disable */
// sorry I have to disable eslint for this file
// native d3 script does not work with eslint......
// Steven - disabled eslint and change const RadarChart -> export

/////////////////////////////////////////////////////////
/////////////// The Radar Chart Function ////////////////
/// mthh - 2017 /////////////////////////////////////////
// Inspired by the code of alangrafu and Nadieh Bremer //
// (VisualCinnamon.com) and modified for d3 v4 //////////
/////////////////////////////////////////////////////////

const max = Math.max;
const sin = Math.sin;
const cos = Math.cos;
const HALF_PI = Math.PI / 2;

function RadarChart(parent_selector, data, options, details) {
    //Wraps SVG text - Taken from http://bl.ocks.org/mbostock/7555321
    const wrap = (text, width) => {
        text.each(function () {
            var text = d3.select(this),
                words = text.text().split(/\s+/).reverse(),
                word,
                line = [],
                lineNumber = 0,
                lineHeight = 1.4, // ems
                y = text.attr("y"),
                x = text.attr("x"),
                dy = parseFloat(text.attr("dy")),
                tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");

            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));
                if (tspan.node().getComputedTextLength() > width) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
                }
            }
        });
    }//wrap

    const cfg = {
        w: 600,				//Width of the circle
        h: 600,				//Height of the circle
        margin: { top: 20, right: 20, bottom: 20, left: 20 }, //The margins of the SVG
        levels: 3,				//How many levels or inner circles should there be drawn
        maxValue: 0, 			//What is the value that the biggest circle will represent
        labelFactor: 1.25, 	//How much farther than the radius of the outer circle should the labels be placed
        wrapWidth: 60, 		//The number of pixels after which a label needs to be given a new line
        opacityArea: 0.35, 	//The opacity of the area of the blob
        dotRadius: 4, 			//The size of the colored circles of each blog
        opacityCircles: 0.1, 	//The opacity of the circles of each blob
        strokeWidth: 2, 		//The width of the stroke around each blob
        roundStrokes: false,	//If true the area and stroke will follow a round path (cardinal-closed)
        color: d3.scaleOrdinal(d3.schemeCategory10),	//Color function,
        format: '.2%',
        unit: '',
        legend: false
    };

    //Put all of the options into a variable called cfg
    if ('undefined' !== typeof options) {
        for (var i in options) {
            if ('undefined' !== typeof options[i]) { cfg[i] = options[i]; }
        }//for i
    }//if

    //If the supplied maxValue is smaller than the actual one, replace by the max in the data
    // var maxValue = max(cfg.maxValue, d3.max(data, function(i){return d3.max(i.map(function(o){return o.value;}))}));
    let maxValue = 0;
    for (let j = 0; j < data.length; j++) {
        for (let i = 0; i < data[j].axes.length; i++) {
            data[j].axes[i]['id'] = data[j].name;
            if (data[j].axes[i]['value'] > maxValue) {
                maxValue = data[j].axes[i]['value'];
            }
        }
    }
    maxValue = max(cfg.maxValue, maxValue);

    const allAxis = data[0].axes.map((i, j) => i.axis),	//Names of each axis
        total = allAxis.length,					//The number of different axes
        radius = Math.min(cfg.w / 2, cfg.h / 2), 	//Radius of the outermost circle
        Format = d3.format(cfg.format),			 	//Formatting
        angleSlice = Math.PI * 2 / total;		//The width in radians of each "slice"

    //Scale for the radius
    const rScale = d3.scaleLinear()
        .range([0, radius])
        .domain([0, maxValue]);

    const parent = d3.select(parent_selector);
    if (typeof (parent_selector) === 'undefined')
        return;
    var width = parent_selector.clientWidth,
        height = parent_selector.clientHeight,
        fontSize = (Math.min(width, height) / 4);

    //Remove whatever chart with the same id/class was present before
    parent.select("svg").remove();

    //Initiate the radar chart SVG
    let svg = parent.append("svg")
        .attr("width", '100%')
        .attr("height", '100%')
        .attr('viewBox', '0 0 ' + width + ' ' + Math.min(width, cfg.h))
        .attr('preserveAspectRatio', 'xMinYMin')
        .attr("class", "radar");

    //Append a g element
    let g = svg.append("g")
        .attr("transform", "translate(" + (width / 2) + "," + (cfg.h / 2) + ")");

    /////////////////////////////////////////////////////////
    ////////// Glow filter for some extra pizzazz ///////////
    /////////////////////////////////////////////////////////

    //Filter for the outside glow
    let filter = g.append('defs').append('filter').attr('id', 'glow'),
        feGaussianBlur = filter.append('feGaussianBlur').attr('stdDeviation', '2.5').attr('result', 'coloredBlur'),
        feMerge = filter.append('feMerge'),
        feMergeNode_1 = feMerge.append('feMergeNode').attr('in', 'coloredBlur'),
        feMergeNode_2 = feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    /////////////////////////////////////////////////////////
    /////////////// Draw the Circular grid //////////////////
    /////////////////////////////////////////////////////////

    //Wrapper for the grid & axes
    let axisGrid = g.append("g").attr("class", "axisWrapper");

    //Draw the background circles
    axisGrid.selectAll(".levels")
        .data(d3.range(1, (cfg.levels + 1)).reverse())
        .enter()
        .append("circle")
        .attr("class", "gridCircle")
        .attr("r", d => radius / cfg.levels * d)
        .style("fill", "#CDCDCD")
        .style("stroke", "#CDCDCD")
        .style("fill-opacity", cfg.opacityCircles)
        .style("filter", "url(#glow)");

    //Text indicating at what % each level is
    axisGrid.selectAll(".axisLabel")
        .data(d3.range(1, (cfg.levels + 1)).reverse())
        .enter().append("text")
        .attr("class", "axisLabel")
        .attr("x", 4)
        .attr("y", d => -d * radius / cfg.levels)
        .attr("dy", "0.4em")
        .style("font-size", "8px")
        .attr("fill", "#737373")
        .text(d => Format(maxValue * d / cfg.levels) + cfg.unit);

    /////////////////////////////////////////////////////////
    //////////////////// Draw the axes //////////////////////
    /////////////////////////////////////////////////////////

    //Create the straight lines radiating outward from the center
    var axis = axisGrid.selectAll(".axis")
        .data(allAxis)
        .enter()
        .append("g")
        .attr("class", "axis");
    //Append the lines
    axis.append("line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", (d, i) => rScale(maxValue * 1.1) * cos(angleSlice * i - HALF_PI))
        .attr("y2", (d, i) => rScale(maxValue * 1.1) * sin(angleSlice * i - HALF_PI))
        .attr("class", "line")
        .style("stroke", "white")
        .style("stroke-width", "2px");

    //Append the labels at each axis
    axis.append("text")
        .attr("class", "legend")
        .style("font-size", "11px")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .attr("x", (d, i) => rScale(maxValue * cfg.labelFactor) * cos(angleSlice * i - HALF_PI))
        .attr("y", (d, i) => rScale(maxValue * cfg.labelFactor) * sin(angleSlice * i - HALF_PI) - 20)
        .text(d => d)
        .call(wrap, cfg.wrapWidth);

    /////////////////////////////////////////////////////////
    ///////////// Draw the radar chart blobs ////////////////
    /////////////////////////////////////////////////////////

    //The radial line function
    const radarLine = d3.radialLine()
        .curve(d3.curveLinearClosed)
        .radius(d => rScale(d.value))
        .angle((d, i) => i * angleSlice);

    if (cfg.roundStrokes) {
        radarLine.curve(d3.curveCardinalClosed)
    }

    //Create a wrapper for the blobs
    const blobWrapper = g.selectAll(".radarWrapper")
        .data(data)
        .enter().append("g")
        .attr("class", "radarWrapper");

    //Append the backgrounds
    blobWrapper
        .append("path")
        .attr("class", "radarArea")
        .attr("d", d => radarLine(d.axes))
        .style("fill", (d, i) => cfg.color(i))
        .style("fill-opacity", cfg.opacityArea)
        .on('mouseover', function (d, i) {
            //Dim all blobs
            parent.selectAll(".radarArea")
                .transition().duration(200)
                .style("fill-opacity", 0.1);
            //Bring back the hovered over blob
            d3.select(this)
                .transition().duration(200)
                .style("fill-opacity", 0.7);
        })
        .on('mouseout', () => {
            //Bring back all blobs
            parent.selectAll(".radarArea")
                .transition().duration(200)
                .style("fill-opacity", cfg.opacityArea);
        });

    //Create the outlines
    blobWrapper.append("path")
        .attr("class", "radarStroke")
        .attr("d", function (d, i) { return radarLine(d.axes); })
        .style("stroke-width", cfg.strokeWidth + "px")
        .style("stroke", (d, i) => cfg.color(i))
        .style("fill", "none")
        .style("filter", "url(#glow)");

    //Append the circles
    blobWrapper.selectAll(".radarCircle")
        .data(d => d.axes)
        .enter()
        .append("circle")
        .attr("class", "radarCircle")
        .attr("r", cfg.dotRadius)
        .attr("cx", (d, i) => rScale(d.value) * cos(angleSlice * i - HALF_PI))
        .attr("cy", (d, i) => rScale(d.value) * sin(angleSlice * i - HALF_PI))
        .style("fill", (d) => cfg.color(d.id))
        .style("fill-opacity", 0.8);

    /////////////////////////////////////////////////////////
    //////// Append invisible circles for tooltip ///////////
    /////////////////////////////////////////////////////////

    //Wrapper for the invisible circles on top
    const blobCircleWrapper = g.selectAll(".radarCircleWrapper")
        .data(data)
        .enter().append("g")
        .attr("class", "radarCircleWrapper");

    //Append a set of invisible circles on top for the mouseover pop-up
    blobCircleWrapper.selectAll(".radarInvisibleCircle")
        .data(d => d.axes)
        .enter().append("circle")
        .attr("class", "radarInvisibleCircle")
        .attr("r", cfg.dotRadius * 1.5)
        .attr("cx", (d, i) => rScale(d.value) * cos(angleSlice * i - HALF_PI))
        .attr("cy", (d, i) => rScale(d.value) * sin(angleSlice * i - HALF_PI))
        .style("fill", "none")
        .style("pointer-events", "all")
        .on("mouseover", function (d, i) {
            tooltip
                .attr('x', this.cx.baseVal.value - 10)
                .attr('y', this.cy.baseVal.value - 10)
                .transition()
                .style('display', 'block')
                .text(Format(d.value) + cfg.unit);
        })
        .on("mouseout", function () {
            tooltip.transition()
                .style('display', 'none').text('');
        })
        .on("click", function (d) {
            details(d);
        });

    const tooltip = g.append("text")
        .attr("class", "tooltip")
        .attr('x', 0)
        .attr('y', 0)
        .style("font-size", "12px")
        .style('display', 'none')
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em");

    if (cfg.legend !== false && typeof cfg.legend === "object") {
        let legendZone = svg.append('g');
        let names = data.map(el => el.name);
        if (cfg.legend.title) {
            let title = legendZone.append("text")
                .attr("class", "title")
                .attr('transform', `translate(${cfg.legend.translateX},${cfg.legend.translateY})`)
                .attr("x", cfg.w - 70)
                .attr("y", 10)
                .attr("font-size", "12px")
                .attr("fill", "#404040")
                .text(cfg.legend.title);
        }
        let legend = legendZone.append("g")
            .attr("class", "legend")
            .attr("height", 100)
            .attr("width", 200)
            .attr('transform', `translate(${cfg.legend.translateX},${cfg.legend.translateY + 20})`);
        // Create rectangles markers
        legend.selectAll('rect')
            .data(names)
        enter()
        ppend("rect")
        attr("x", cfg.w - 65)
        attr("y", (d, i) => i * 20)
        attr("width", 10)
        attr("height", 10)
        style("fill", (d, i) => cfg.color(i));
        // Create labels
        legend.selectAll('text')
        data(names)
        nter()
            .append("text")
            .attr("x", cfg.w - 52)
            .attr("y", (d, i) => i * 20 + 9)
            .attr("font-size", "11px")
            .attr("fill", "#737373")
            .text(d => d);
    }
    return svg;
}

export class RadarD3 extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            modalDetails: false,
            modal: {},
            items: props.items || [],
            limit: props.limit || 8,
            map: {}
        }
    }

    componentDidMount() {
        get_resource(this.props.data, map => {
            this.setState({ map: map });
            setTimeout(() => this.drawChart(), 100);
        })
    }

    drawChart() {
        // var data = [
        //     // {
        //     //     name: 'Allocated budget',
        //     //     axes: [
        //     //         { axis: 'Sales', value: 42 },
        //     //         { axis: 'Marketing', value: 20 },
        //     //         { axis: 'Development', value: 60 },
        //     //         { axis: 'Customer Support', value: 26 },
        //     //         { axis: 'Information Technology', value: 35 },
        //     //         { axis: 'Administration', value: 20 }
        //     //     ]
        //     // },
        //     {
        //         name: 'Actual Spending',
        //         axes: [
        //             { axis: 'Sales', value: 50 },
        //             { axis: 'Marketing', value: 45 },
        //             { axis: 'Development', value: 20 },
        //             { axis: 'Customer Support', value: 20 },
        //             { axis: 'Information Technology', value: 25 },
        //             { axis: 'Administration', value: 23 }
        //         ]
        //     }
        // ];
        console.log('drawing....')

        var data = [];
        // var items = [];
        for (let key in this.props.data) {
            let res = this.props.data[key]
            let axes = [];
            for (let i = 0; i < Math.min(res.x.length, this.state.limit); ++i) {
                if (res.y[i] <= 1)
                    res.y[i] *= 100
                let attr = this.state.map[res.x[i]];
                let name = attr.tags + ' ' + attr.name
                axes.push({ 'axis': name.substring(0, 30), 'value': res.y[i], 'attr': attr })
            }
            // items.push({ 'name': key, '_id': res._id, '_view': res._view })
            data.push({ 'name': key, 'axes': axes })
        }
        // this.setState({ items: items })


        var radarChartOptions = {
            w: 200,
            h: 300,
            margin: { top: 20, right: 20, bottom: 20, left: 0 },
            levels: 5,
            roundStrokes: true,
            color: d3.scaleOrdinal().range(["#ff6600", "#AFC52F"]),
            format: '.0f'
        };

        RadarChart(
            this.refs.chart,
            data,
            radarChartOptions,
            d => {
                console.log(d);
                this.setState({ modal: d })
                this.toggleDetails();
            }
        );
    }


    toggleDetails = () => {
        this.setState({
            modalDetails: !this.state.modalDetails
        })
    }

    render() {
        return (<>
            <Card className="card-chart">
                <CardHeader>
                    {
                        this.props.name.split('-').map(vs => (
                            <h5 key={vs}>{vs}</h5>))
                    }
                    <h5 className="card-category" key='note'>Showing top-{this.state.limit} results. </h5>
                </CardHeader>
                <CardBody>
                    <Row>
                        <Col md="12">
                            <div className='d3-container-sm' ref="chart">

                            </div>
                        </Col>
                        {/* <Col md="12">
                            <Row className='items-row'>
                                {typeof (this.state.items) !== 'undefined' ? this.state.items.map((item, k0) =>
                                    item._id.map((_, k) => {
                                        var View = templates[item._view[k]];
                                        return typeof (View) === 'undefined' ? null : (<Col md={3}><View key={k0 + '-' + k} size='sm' rid={item._id[k]} /></Col>)
                                    }
                                    )
                                ) : <></>}
                            </Row>
                        </Col> */}
                    </Row>
                    <Modal isOpen={this.state.modalDetails} toggle={this.toggleDetails}>
                        <div className="modal-header">
                            <h5 className="modal-title" id="exampleModalLabel">More Details</h5>
                            <button
                                type="button"
                                className="close"
                                data-dismiss="modal"
                                aria-hidden="true"
                                onClick={this.toggleDetails}
                            >
                                <i className="tim-icons icon-simple-remove" />
                            </button>
                        </div>
                        <ModalBody className='chart-modal'>
                            {/* <p>Detailed information of the match.</p> */}
                            <pre>
                                {JSON.stringify(this.state.modal, null, '\t')}
                            </pre>
                        </ModalBody>
                    </Modal>
                </CardBody>
            </Card>
        </>
        )
    }
}

export default RadarD3;
