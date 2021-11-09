/*!

=========================================================
* Black Dashboard React v1.0.0
=========================================================

* Product Page: https://www.creative-tim.com/product/black-dashboard-react
* Copyright 2019 Creative Tim (https://www.creative-tim.com)
* Licensed under MIT (https://github.com/creativetimofficial/black-dashboard-react/blob/master/LICENSE.md)

* Coded by Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/
import React from "react";
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem, TabPane, Table, Nav, NavItem, TabContent, CardText, CardTitle, NavLink, Collapse, CardColumns } from 'reactstrap';
import PerfectScrollbar from "perfect-scrollbar";
import axios from 'axios';
import Typewriter from 'typewriter-effect';
import queryString from 'query-string';
import SystemFlow from '../components/System/sys'
import { withRouter } from "react-router-dom";
import Plot from 'react-plotly.js';
import Split from 'react-split'
// reactstrap components
import {
  Button,
  Card,
  CardHeader,
  Row,
  Col
} from "reactstrap";
import { typeOf, } from "mathjs";
import { ax, urlfor } from "../api.js";

import { Line } from "react-chartjs-2";
import "chartjs-plugin-streaming";
import { Sparklines, SparklinesLine, SparklinesSpots } from 'react-sparklines';





/** Mission is used for showing result of file analysis*/
class Mission extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      phase: 0, // 0 - prepare 1 - running 2 - stopped and waiting to return
      // detailed information of all the guages
      guages: [],
      // numeric guages
      streams: [],
      // location-based guages
      maps: [],
      // bc guage
      bc: [],
      // current data reading
      data: [],
      // query interval object
      query_si: -1,
      // intrusion detection
      ids: [[], [], []],
      // all attacks:
      attks: [],
      layout: {
        datarevision: 0,
      },
      revision: 0,
    };
  }

  componentDidMount = () => {
    //setup scroll bar
    // if (navigator.platform.indexOf("Win") > -1) {
    document.documentElement.className += " perfect-scrollbar-on";
    document.documentElement.classList.remove("perfect-scrollbar-off");
    new PerfectScrollbar(this.refs.mainPanel, { suppressScrollX: true });
    // }


    ax.get('/api/get_sim').then(res => {
      if (res.data) {
        console.log(res.data)
        // system not running
        if ('err' in res.data) {
          // reaching this page without running system
          this.props.history.push("/")
        } else if (res.data.running) {
          // running 
          this.setState({ phase: 1 })
        } else if (res.data.running) {
          // stopped
          this.setState({ phase: 0 })
        }
      }
    })

    ax.get('/api/get_guages').then(res => {
      if (res.data) {
        this.setState({ guages: res.data })
        let streams = [];

        let maps = [];
        // store the index (as the id) for each guage
        for (let i = 0; i < res.data.length; ++i) {
          let g = res.data[i];
          if (g.name.includes('gps'))
            maps.push(i);
          else if (g.name.includes('bc'))
            this.setState({ bc: i })
          else
            streams.push(i)
          this.setState({ streams: streams })
        }
      }
    })
    ax.get('api/list_attacks').then(res => {
      if (res.data) {
        this.setState({ attks: res.data })
      }
    })
    console.log('here!')
    let si = setInterval(() => {
      ax.get('/api/read_guages').then(res => {
        if (res.data) {
          this.setState({ data: res.data });
        }
      })

      ax.get('/api/read_ids').then(res => {
        if (res.data && res.data.length > 0) {
          // this.setState({ ids: res.data })
          const ids = this.state.ids;
          var time = new Date();
          var olderTime = time.setMinutes(time.getMinutes() - 1);
          var futureTime = time.setMinutes(time.getMinutes() + 1);
          let arr = res.data;
          let t = '';
          ids[0].push(time);
          ids[1].push(arr[0]);
          if (arr[0] > 0.5)
            t = this.state.attks[arr.indexOf(Math.max(...arr.slice(1)))].name
          ids[2].push(t)

          this.setState({
            ids: ids, layout: {
              datarevision: ids[0].length,
              autosize: true,
              xaxis: {
                type: 'date',
                range: [olderTime, futureTime],
                "gridcolor": "#283442",
                "linecolor": "#506784",
                "automargin": true,
                "zerolinecolor": "#283442",
                "zerolinewidth": 2,
              },
              yaxis: {
                range: [-0.1, 1.1],
                "gridcolor": "#283442",
                "linecolor": "#506784",
                "automargin": true,
                "zerolinecolor": "#283442",
                "zerolinewidth": 2
              },
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
              "mapbox": {
                "style": "dark"
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
              "plot_bgcolor": "rgba(17,17,17,.3)",
              "paper_bgcolor": "rgba(17,17,17,.3)",
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
              },
              margin: { l: 0, r: 0, t: 10, b: 10 },
            },
            revision: ids[0].length,
          })
          console.log(this.state)
        }
      })
    }, 500);
    this.setState({ query_si: si })

  }


  componentWillUnmount() {
    clearInterval(this.state.query_si);
  }


  create_header() {
    return (
      <>
        <div className="col-sm-12 g-panel g-header" >
          <Button className="btn btn-sm btn-info pull-left" onClick={() => {
            if (this.state.phase == 0) {
              ax.post('api/takeoff')
              this.setState({ phase: 1 })
            }
            else if (this.state.phase == 1) {
              ax.post('api/stop')
              clearInterval(this.state.query_si)
              this.setState({ phase: 2 })
            }
            else {
              this.props.history.push("/")
            }
          }}>{{ 0: 'Take off', 1: 'Stop', 2: 'Exit' }[this.state.phase]}</Button>
        </div>
        {/*End of NavBar of Mission page */}
      </>)
  }

  create_ids_chart = () => {
    const data = canvas => {
      let ctx = canvas.getContext("2d");
      let gradientStroke = ctx.createLinearGradient(0, canvas.parentElement.offsetHeight * 1.2, 0, 50);
      gradientStroke.addColorStop(1, "rgba(72,72,176,.4)");
      gradientStroke.addColorStop(0.5, "rgba(72,72,176,0.2)");
      gradientStroke.addColorStop(0, "rgba(119,52,169,0)"); //purple colors
      let ds = [];
      for (let i = 0; i < 10 + 1; ++i) {
        ds.push({
          fill: true,
          backgroundColor: gradientStroke,
          borderColor: "#d048b6",
          borderWidth: 0,
          borderDash: [],
          borderDashOffset: 0.0,
          pointRadius: 0,
          label: i == 0 ? 'anomaly' : 'a',
          data: [],
        })
        break;
      }

      return {
        datasets: ds
      }
    }

    const options = {
      legend: {
        display: false
      },
      tooltips: {
        enabled: false
      },
      scales: {
        yAxes: [
          {
            ticks: {
              display: true, //this will remove only the label,
              min: -0.1,
              max: 1.1,
            },
            gridLines: {
              display: true
            }
          }],
        xAxes: [
          {
            ticks: {
              display: true //this will remove only the label
            },
            gridLines: {
              display: true
            },
            type: "realtime",
            realtime: {
              onRefresh: (chart) => {
                chart.data.datasets[0].data.push({
                  x: Date.now(),
                  y: Math.random()
                });
                console.log(chart.data.datasets[0].data)
                // ax.get('/api/read_ids').then(res => {
                //   if (res.data && res.data.length > 0) {
                //     for (let i = 0; i < res.data.length; ++i)
                //       chart.data.datasets[i].data.push({
                //         x: Date.now(),
                //         y: Math.random()
                //       });
                //   }
                // })
              },
              delay: 3000,
              refresh: 1000,
              duration: 10000,
            }
          }
        ]
      }
    };
    return (<Line data={data} options={options} height="300px" />)
  }

  create_value(g_id, s_id) {
    if (this.state.data[g_id]) {
      let v = this.state.data[g_id][s_id]
      if (v && v.toFixed)
        return v.toFixed(2);
    }
    return 'n/a'
  }

  create_guage = g_id => {
    let g = this.state.guages[g_id]
    return (
      <div className='col col-sm col-sm-12 g-panel'>
        <h5>{g.name}</h5>
        <Row>
          {g.sources.map((s, s_id) =>
            <div className='col col-sm col-sm-6'>
              <h6 className='g-label'>{s}</h6>
              {/* {this.create_chart(g_id, s_id)} */}
              {this.create_value(g_id, s_id)}
            </div>
          )}
        </Row>
      </div>
    )
  }

  render() {
    return (
      <>
        <img src={urlfor('api/video_feed')} className='stream-bg' />
        <div className="wrapper">
          <div className="main-panel" ref="mainPanel" >
            <div className="single-content">
              <Row>
                {this.create_header()}
              </Row>
              <Row style={{ minHeight: '95vh' }}>
                <div className='col col-md col-md-3' >
                  <Row>
                    {this.state.streams.map(g_id => this.create_guage(g_id))}
                  </Row>
                </div>
                <div className='col col-md col-md-9'>
                  <Row style={{ minHeight: '55vh' }}>
                    <div className='col col-md col-md-12 split-holder'>
                      <Split className='split' sizes={[60, 40]} gutterSize={6}
                        gutterAlign="center" minSize={30}>
                        <div style={{ height: 100 }}></div>
                        <SystemFlow></SystemFlow>
                      </Split>
                    </div>
                  </Row>
                  <Row style={{ minHeight: '35vh', marginTop: 15 }}>
                    <div className='col col-md col-md-12 split-holder'>
                      <Split className='split' sizes={[50, 50]} gutterSize={6}
                        gutterAlign="center" minSize={30}>
                        <div style={{ height: 100 }}></div>
                        <div className='g-panel-right'>
                          {/* <Sparklines data={this.state.ids[0]} limit={600}>
                            <SparklinesLine color="#1c8cdc" />
                            <SparklinesSpots />
                          </Sparklines> */}
                          {/* {this.create_ids_chart()} */}
                          {this.state.ids[0] ?
                            <Plot
                              data={[
                                {
                                  x: this.state.ids[0],
                                  y: this.state.ids[1],
                                  text: this.state.ids[2],
                                  type: 'scatter',
                                  mode: 'lines+markers',
                                  marker: { color: 'red' },
                                },
                              ]}
                              layout={this.state.layout}
                              revision={this.state.revision}
                              style={{ width: "100%", height: "100%", minWidth: "100" }}
                            // layout={{ width: 320, height: 240, title: 'A Fancy Plot' }}
                            /> : null}
                        </div>
                      </Split>
                    </div>
                  </Row>
                </div>
              </Row>
            </div>
          </div>
        </div>
      </>
    );
  }
}

export default withRouter(Mission);