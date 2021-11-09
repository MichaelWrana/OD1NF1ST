
import React from "react";
// nodejs library that concatenates classes
import classNames from "classnames";
// react plugin used to create charts
import { Line, Bar } from "react-chartjs-2";
import { withRouter } from "react-router-dom";

// reactstrap components
import {
  Button,
  ButtonGroup,
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  UncontrolledDropdown,
  Label,
  FormGroup,
  Input,
  Table,
  Row,
  Col,
  UncontrolledTooltip,
  CardFooter
} from "reactstrap";

import PerfectScrollbar from "perfect-scrollbar";
import axios from 'axios';
import { lineChartOptions, barChartOptions, wrapDataForLineChart, statusdesp2icon, status2icon, mission2icon } from '../variables/charts.jsx'


class Cyberdeck extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      //default timeline is submitted
      status_timeline_active: "submitted",
      //load relevant squad data to cyberdeck component
      selected_type: props.selected_type,
      theme: props.theme,
      data: props.data,
      recent_missions: props.recent_missions,
      recent_missions_page: 1,
      pinned_missions: props.pinned_missions,
      nodes: props.nodes,
    };
  }

  componentDidUpdate = (previousProp, previousState) => {
    //setup custom scrollbar
    if (navigator.platform.indexOf("Win") > -1) {
      let tables = document.querySelectorAll(".table-responsive");
      for (let i = 0; i < tables.length; i++) {
        new PerfectScrollbar(tables[i]);
      }
    }

    //if squad is changed, need to update mission status
    if (previousState.selected_type !== this.state.selected_type) {
      this.setState({ recent_missions_page: 1 })
      this.update_recent_table()
    } else if (previousState.recent_missions_page !== this.state.recent_missions_page) {
      if (this.state.recent_missions_page > 0)
        this.update_recent_table()
    }
  }

  //get mission status from API call and load into this component's state
  update_recent_table = () => axios.get('/api/report/get_by_uid', {
    params: {
      uid: 'general',
      recent: 10,
      mission: this.state.selected_type,
      page: this.state.recent_missions_page || 1
    }
  }).then(data => {
    if (data.data.length > 0)
      this.setState({
        recent_missions: data.data,
      })
    else
      this.setState({
        recent_missions_page: this.state.recent_missions_page === 1 ? 1 : this.state.recent_missions_page - 1
      })
  })
  //Retrieving Squad History
  componentDidMount() {
    //get mission stats from API call and load into component's state
    axios.get('/api/report/get_stats').then(data => {
      console.log(data.data);
      let key = data.data.default_key;
      if (!(key in data.data.types_trooper_time_percentiles)) {
        key = Object.keys(data.data.types_trooper_time_percentiles)[0];
      }
      this.setState({
        data: data.data,
        selected_type: key
      })
      this.update_recent_table()
    });

    axios.get('/api/nodes').then(data => {
      console.log(data);
      this.setState({ nodes: data.data })
    })


    //setup custom scrollbar
    if (navigator.platform.indexOf("Win") > -1) {
      let tables = document.querySelectorAll(".table-responsive");
      for (let i = 0; i < tables.length; i++) {
        new PerfectScrollbar(tables[i]);
      }
    }

  }
  /*Loading screen for all processes */
  loading_view = () => {
    return (<Row><Col lg="12"><h1 className="text-center jarv1s">Loading... </h1></Col></Row>)
  }


  selected_type_percentile_data = () =>
    this.state.data.types_trooper_time_percentiles[
    this.state.selected_type
    ]

  /*Renders homepage i.e. cyberdeck */
  ready_view = () => {
    return (
      <>
        {/*Beginning of Timeline Card */}
        <Row>
          <Col xs="12">
            <Card className="card-chart mission-status">
              <CardHeader>
                <Row>
                  <Col className="text-left" sm="6">
                    <h5 className="card-description">
                      Mission Submissions:
                    </h5>
                    <CardTitle tag="h2">Timeline</CardTitle>
                  </Col>
                  <Col sm="6">
                    <ButtonGroup
                      className="btn-group-toggle float-right"
                      data-toggle="buttons"
                    >

                      {Object.entries(this.state.data.status_timeline).map((v, k) => (
                        <Button
                          tag="label"
                          className={classNames("btn-simple", {
                            active: this.state.status_timeline_active === v[0]
                          })}
                          color="info"
                          id="0"
                          size="sm"
                          onClick={() => this.setState({ status_timeline_active: v[0] })}
                        >
                          <input
                            defaultChecked
                            className="d-none"
                            name="options"
                            type="radio"
                          />
                          <span className="d-none d-sm-block d-md-block d-lg-block d-xl-block">
                            {v[0]}
                          </span>
                          <span className="d-block d-sm-none">
                            {statusdesp2icon[v[0]]}
                            <i className="tim-icons icon-single-02" />
                          </span>
                        </Button>

                      ))}

                    </ButtonGroup>
                  </Col>
                </Row>
              </CardHeader>
              <CardBody>
                <Row>
                  <Col sm="12">
                    <div className="chart-area">
                      <Line
                        data={/*Visual timeline of file submissions*/wrapDataForLineChart(
                          this.state.data.status_timeline[this.state.status_timeline_active],
                          this.state.status_timeline_active,
                          this.state.theme)}
                        options={lineChartOptions}
                      />
                    </div>
                  </Col>
                </Row>
              </CardBody>
              <CardFooter>
                <Row>
                  <Col className="text-right">
                    <h5 className="card-category">
                      Document Store: &nbsp;
                      {Object.entries(this.state.data.all_counts).map((v, k) => {
                      return <>{v[0]}={v[1]} &nbsp; </>
                    })}
                    </h5>
                  </Col>
                </Row>
                <Row>
                  <Col className="text-right">
                    <h5 className="card-category">
                      Mission Status: &nbsp;
                      {this.state.data.status_counter.labels.map((v, k) => {
                      return (<>{status2icon[v]}&nbsp;{v}={this.state.data.status_counter.values[k]} &nbsp; &nbsp;</>)
                    })}
                    </h5>
                  </Col>
                </Row>
              </CardFooter>
            </Card>
          </Col>
        </Row>
        {/*End of Timeline Card */}
        {/*Beginning of History Card */}
        <Row>
          <Col lg="12">
            <Card className="card-chart">
              <CardHeader>
                <h5 className='card-category'> {this.state.selected_squad}</h5>
                <h5 className="card-description"> Execution History  </h5>
                <UncontrolledDropdown>
                  <DropdownToggle
                    caret
                    className="btn-info"
                    color="link"
                    data-toggle="dropdown"
                    type="button"
                  >
                    <h5 className='text-danger'>  Select Mission Type &nbsp;<i className="tim-icons icon-settings-gear-63" /> </h5>
                  </DropdownToggle>
                  <DropdownMenu aria-labelledby="dropdownMenuLink" className="dropdown-black" right>
                    {Object.keys(this.state.data.types_time_percentiles).map((v, k) => (
                      <DropdownItem
                        href="#pablo"
                        id={v}
                        onClick={e => {
                          this.setState({
                            selected_type: v
                          });
                          e.preventDefault();
                        }}
                      >
                        {v}
                      </DropdownItem>
                    ))}
                  </DropdownMenu>
                </UncontrolledDropdown>
              </CardHeader>
              <CardBody>
                <Row>
                  <Col sm='7'>
                    <div className="table-full-width table-responsive table-compact">
                      <div className='pull-right table-handle'>
                        <i className="fas fa-caret-left" onClick={e => { e.preventDefault(); if (this.state.recent_missions_page > 1) this.setState({ recent_missions_page: this.state.recent_missions_page - 1 }) }}></i>
                      &nbsp;&nbsp;{this.state.recent_missions_page}&nbsp;&nbsp;
                      <i className="fas fa-caret-right" onClick={e => { e.preventDefault(); this.setState({ recent_missions_page: this.state.recent_missions_page + 1 }) }}></i>
                      </div>
                      <Table>
                        <thead>
                        </thead>
                        <tbody>
                          {
                            typeof (this.state.recent_missions) === 'undefined' ? null :
                              this.state.recent_missions.map((v, k) =>
                                (
                                  <>
                                    <tr key={this.state.selected_squad + k}>
                                      <td>{mission2icon[v.mission]}</td>
                                      <td>{v.submitted}</td>
                                      <td className='history-label'>{typeof (v.label) === 'undefined' ? (v._id.substring(0, 15) + '...') : (v.label)}</td>
                                      <td>{status2icon[v.status]}</td>
                                      <td>
                                        <a href={`/mission?mid=${v._id}`} title='details' target="_blank" >
                                        {/* <a href={`/mission?mid=${v._id}`} onClick={e=>{e.preventDefault();this.props.history.push(`/mission?mid=${v._id}`);}} title='details' target="_blank" > */}
                                          <i className="tim-icons icon-molecule-40 text-primary"></i></a>
                                      </td>
                                      <td>{v.taken}s</td>
                                    </tr>
                                  </>
                                )
                              )
                          }
                        </tbody>
                      </Table>
                    </div>
                  </Col>
                  <Col sm='5'>
                    <h5 className='card-category'>Execution time composition (CDF)</h5>
                    <div className="chart-area extra-height">
                      {/* <Line
                            key={this.state.selected_squad}
                            data={wrapDataForLineChart(
                              this.state.data.types_time_percentiles[
                              this.state.selected_squad
                              ],
                              'time-taken (seconds)',
                              this.state.theme
                            )}
                            options={lineChartOptions}
                          /> */}
                      {this.state.selected_type in this.state.data.types_trooper_time_percentiles ?
                        <Bar
                          key={this.state.selected_type}
                          data={wrapDataForLineChart(
                            Object.values(this.selected_type_percentile_data()),
                            Object.keys(this.selected_type_percentile_data()),
                          )}
                          options={barChartOptions}
                        />
                        : null}
                    </div>
                  </Col>
                </Row>
              </CardBody>
            </Card>

          </Col>
        </Row >
        {/*End of Squad History Card */}

        {/*End of Latest Flow Chart Card */}
        {/*Beginning of Execution Time Distribution cards */}
        <Row>

          {
            !(this.state.selected_type in this.state.data.types_trooper_time_percentiles) ? null :
              Object.entries(this.state.data.types_trooper_time_percentiles[
                this.state.selected_type
              ]).sort((a, b) => Math.max.apply(this, a.values) - Math.max.apply(this, b.values)).map((v, k) => (<>
                <Col sm='4'>
                  <Card className='card-chart'>
                    <CardHeader>
                      <h5 className='card-category'> {this.state.selected_type}</h5>
                      <h5 className='card-description'>{v[0]}</h5>
                    </CardHeader>
                    <CardBody>
                      <div className="chart-area">
                        <Line
                          key={this.state.selected_type + k}
                          data={wrapDataForLineChart(v[1], v[0], this.state.theme)}
                          options={lineChartOptions}
                        />
                      </div>
                      <h5 className='card-description text-center'>Trooper Execution Time Distribution (CDF)</h5>
                    </CardBody>
                  </Card>
                </Col>
              </>))}

        </Row>
        {/*End of Execution Time Distribution cards */}

        {/*Beginning of Latest Flow Chart Card 
        Do not render if user has never submitted a file*/}
        {typeof (this.state.nodes) === 'undefined' ? null : (
          <Row>
            <Col sm='12' >
              <Card className='flow-card'>
                <CardHeader>
                  <h5 className='card-category'>Full execution graph</h5>
                  <h5 className='card-description'>Including all the executors.</h5>
                </CardHeader>
                <CardBody>
                </CardBody>
              </Card>
            </Col>
          </Row>
        )}
      </>
    );
  }

  render() {
    return (
      <>
        <div className="content">
          {typeof (this.state.data) === 'undefined' ? this.loading_view() : this.ready_view()}
        </div>
      </>
    )
  }
}

export default withRouter(Cyberdeck);
