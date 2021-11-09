import React from 'react';
import Plot from 'react-plotly.js';
import Plotly from 'plotly.js'
import {
    Card,
    CardHeader,
    CardBody,
    Row,
    Col
} from "reactstrap";

var symbol = Plotly.PlotSchema.get()
    .traces
    .scatter
    .attributes
    .marker
    .symbol
    .values
    .filter(s => typeof s === 'string')

export class Scatter extends React.Component {

    transform_data = () => {
        console.log(this.props.data)
        let data = {}
        let ind = 0
        for (let query of this.props.data.vectors) {
            // let label = query.tags.join(', ')
            let label = query.lb;
            if (!(label in data)) {
                ind += 1
                data[label] = {
                    x: [], y: [], z: [], text: [],
                    mode: 'markers',
                    type: 'scatter3d',
                    name: label,
                    marker: {
                        size: 4,
                        symbol: symbol[ind % symbol.length]
                    }
                }
            }
            data[label].x.push(query.vec[0]);
            data[label].y.push(query.vec[1]);
            data[label].z.push(query.vec[2]);
            data[label].text.push(query.x);
        }
        return Object.values(data)
    }

    render() {
        let data = this.transform_data();
        return (
            <>
                <Col lg="12" className="col">
                    <Card className="card-chart card-chart-scatter" style={{ display: 'block', columnSpan: 'all' }}>
                        <CardHeader>
                            {
                                this.props.name.split('-').map(vs => (
                                    <h5 className="card-category">{vs}</h5>))
                            }
                        </CardHeader>
                        <CardBody>
                            <Plot
                                data={
                                    data
                                }

                                config={
                                    { responsive: true }
                                }

                                // layout={{ width: 320, height: 240, title: 'A Fancy Plot' }}
                                layout={{
                                    "geo": {
                                        "bgcolor": "rgb(17,17,17)",
                                        "showland": true,
                                        "lakecolor": "rgb(17,17,17)",
                                        "landcolor": "rgb(17,17,17)",
                                        "showlakes": true,
                                        "subunitcolor": "#506784"
                                    },
                                    "font": {
                                        "color": "#f2f5fa"
                                    },
                                    "polar": {
                                        "bgcolor": "rgb(17,17,17)",
                                        "radialaxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "linecolor": "#506784"
                                        },
                                        "angularaxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "linecolor": "#506784"
                                        }
                                    },
                                    "scene": {
                                        "xaxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "gridwidth": 2,
                                            "linecolor": "#506784",
                                            "zerolinecolor": "#C8D4E3",
                                            "showbackground": true,
                                            "backgroundcolor": "rgb(17,17,17)"
                                        },
                                        "yaxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "gridwidth": 2,
                                            "linecolor": "#506784",
                                            "zerolinecolor": "#C8D4E3",
                                            "showbackground": true,
                                            "backgroundcolor": "rgb(17,17,17)"
                                        },
                                        "zaxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "gridwidth": 2,
                                            "linecolor": "#506784",
                                            "zerolinecolor": "#C8D4E3",
                                            "showbackground": true,
                                            "backgroundcolor": "rgb(17,17,17)"
                                        }
                                    },
                                    "title": {
                                        "x": 0.05
                                    },
                                    "xaxis": {
                                        "ticks": "",
                                        "gridcolor": "#283442",
                                        "linecolor": "#506784",
                                        "automargin": true,
                                        "zerolinecolor": "#283442",
                                        "zerolinewidth": 2
                                    },
                                    "yaxis": {
                                        "ticks": "",
                                        "gridcolor": "#283442",
                                        "linecolor": "#506784",
                                        "automargin": true,
                                        "zerolinecolor": "#283442",
                                        "zerolinewidth": 2
                                    },
                                    "mapbox": {
                                        "style": "dark"
                                    },
                                    "ternary": {
                                        "aaxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "linecolor": "#506784"
                                        },
                                        "baxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "linecolor": "#506784"
                                        },
                                        "caxis": {
                                            "ticks": "",
                                            "gridcolor": "#506784",
                                            "linecolor": "#506784"
                                        },
                                        "bgcolor": "rgb(17,17,17)"
                                    },
                                    "colorway": [
                                        "#636efa",
                                        "#EF553B",
                                        "#00cc96",
                                        "#ab63fa",
                                        "#FFA15A",
                                        "#19d3f3",
                                        "#FF6692",
                                        "#B6E880",
                                        "#FF97FF",
                                        "#FECB52"
                                    ],
                                    "hovermode": "closest",
                                    "colorscale": {
                                        "diverging": [
                                            [
                                                0,
                                                "#8e0152"
                                            ],
                                            [
                                                0.1,
                                                "#c51b7d"
                                            ],
                                            [
                                                0.2,
                                                "#de77ae"
                                            ],
                                            [
                                                0.3,
                                                "#f1b6da"
                                            ],
                                            [
                                                0.4,
                                                "#fde0ef"
                                            ],
                                            [
                                                0.5,
                                                "#f7f7f7"
                                            ],
                                            [
                                                0.6,
                                                "#e6f5d0"
                                            ],
                                            [
                                                0.7,
                                                "#b8e186"
                                            ],
                                            [
                                                0.8,
                                                "#7fbc41"
                                            ],
                                            [
                                                0.9,
                                                "#4d9221"
                                            ],
                                            [
                                                1,
                                                "#276419"
                                            ]
                                        ],
                                        "sequential": [
                                            [
                                                0,
                                                "#0d0887"
                                            ],
                                            [
                                                0.1111111111111111,
                                                "#46039f"
                                            ],
                                            [
                                                0.2222222222222222,
                                                "#7201a8"
                                            ],
                                            [
                                                0.3333333333333333,
                                                "#9c179e"
                                            ],
                                            [
                                                0.4444444444444444,
                                                "#bd3786"
                                            ],
                                            [
                                                0.5555555555555556,
                                                "#d8576b"
                                            ],
                                            [
                                                0.6666666666666666,
                                                "#ed7953"
                                            ],
                                            [
                                                0.7777777777777778,
                                                "#fb9f3a"
                                            ],
                                            [
                                                0.8888888888888888,
                                                "#fdca26"
                                            ],
                                            [
                                                1,
                                                "#f0f921"
                                            ]
                                        ],
                                        "sequentialminus": [
                                            [
                                                0,
                                                "#0d0887"
                                            ],
                                            [
                                                0.1111111111111111,
                                                "#46039f"
                                            ],
                                            [
                                                0.2222222222222222,
                                                "#7201a8"
                                            ],
                                            [
                                                0.3333333333333333,
                                                "#9c179e"
                                            ],
                                            [
                                                0.4444444444444444,
                                                "#bd3786"
                                            ],
                                            [
                                                0.5555555555555556,
                                                "#d8576b"
                                            ],
                                            [
                                                0.6666666666666666,
                                                "#ed7953"
                                            ],
                                            [
                                                0.7777777777777778,
                                                "#fb9f3a"
                                            ],
                                            [
                                                0.8888888888888888,
                                                "#fdca26"
                                            ],
                                            [
                                                1,
                                                "#f0f921"
                                            ]
                                        ]
                                    },
                                    "hoverlabel": {
                                        "align": "left"
                                    },
                                    "plot_bgcolor": "rgb(17,17,17)",
                                    "paper_bgcolor": "rgb(17,17,17)",
                                    "shapedefaults": {
                                        "line": {
                                            "color": "#f2f5fa"
                                        }
                                    },
                                    "sliderdefaults": {
                                        "bgcolor": "#C8D4E3",
                                        "tickwidth": 0,
                                        "bordercolor": "rgb(17,17,17)",
                                        "borderwidth": 1
                                    },
                                    "annotationdefaults": {
                                        "arrowhead": 0,
                                        "arrowcolor": "#f2f5fa",
                                        "arrowwidth": 1
                                    },
                                    "updatemenudefaults": {
                                        "bgcolor": "#506784",
                                        "borderwidth": 0
                                    }
                                }}
                            />
                        </CardBody>
                    </Card>
                    {Object.keys(data).length < 2 ? <></> :
                        <Card >
                            <CardHeader>
                                {
                                    this.props.name.split('-').map(vs => (
                                        <h5 className="card-category">{vs + ' [Cluster Tree View]'}</h5>))
                                }
                            </CardHeader>
                            <CardBody>
                                <div className='Tree'>
                                    {Object.keys(data).map(k => <ul key={k}>
                                        <li key={k}>{'Cluster ' + k}</li>
                                        {data[k].text.map(t => <li key={t}>{t}</li>)}
                                    </ul>)}
                                </div>
                            </CardBody>
                        </Card>
                    }
                </Col>
            </>
        );
    }
}