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
import Typewriter from 'typewriter-effect';
import { withRouter } from "react-router-dom";
import { ax, urlfor } from '../../api'
import { Carousel } from '../../components/carousel/carousel'
import { Collapse } from "reactstrap";


class Landing extends React.Component {
  constructor(props) {
    super(props)
    this.transitionEnd = this.transitionEnd.bind(this)
    this.mountStyle = this.mountStyle.bind(this)
    this.unMountStyle = this.unMountStyle.bind(this)
    this.scene_selector = React.createRef();
    this.state = { //base css
      page: 'START',
      message: '',
      slides: [],
      show: true,
      scenes: [],
      style: {
        opacity: 0,
        transition: 'all 2s ease',
      }
    }
  }
  componentWillLeave() { // check for the mounted props
    this.setState({ // remount the node when the mounted prop is true
      show: true
    })
    setTimeout(this.mountStyle, 10) // call the into animation
  }

  unMountStyle() { // css for unmount animation
    this.setState({
      style: {
        opacity: 0,
        transition: 'all 1s ease',
      }
    })
  }

  mountStyle() { // css for mount animation
    this.setState({
      style: {
        opacity: 1,
        transition: 'all 1s ease',
      }
    })
  }

  componentDidMount() {
    ax.get(
      'api/get_scenes'
    ).then(res => {
      if (res.data) {
        this.setState({ scenes: res.data });
        this.setState({ slides: res.data.map((v, k) => <img src={urlfor(v.thumbnail)} alt={k}></img>) })
        console.log(this.state)
      }
    })
    setTimeout(this.mountStyle, 10) // call the into animation
  }

  transitionEnd() {
    if (!this.props.mounted) { // remove the node on transition end when the mounted prop is false
      this.setState({
        show: false
      })
    }
  }

  get_message = () => {
    switch (this.state.page) {
      case 'START':
        return '<<< START >>>';
      case 'RUN':
        let selected = this.state.scenes[this.scene_selector.current.state.slideCurrent];
        return `<<< Run scene ${selected.name} >>>`
      case 'LOAD':
        return this.state.message
      default:
        break;
    }
  }

  render() {
    return (
      <>
        <div className="offline-doc landing" style={this.state.style} onTransitionEnd={this.transitionEnd}>
          {this.state.scenes.length > 0 ?
            <video autoPlay muted loop id="landing-bg">
              <source src={urlfor(this.state.scenes[0].video) + '#'} type="video/mp4" />
            </video> : null}
          <div className="page-header clear-filter">
            <div className="page-header-image"></div>
            <div className="content-center">
              <div className="col-md-10 ml-auto mr-auto">
                <div className="brand">
                  <h1 className="title jarv1s">
                    <Typewriter onInit={(typewriter) => {
                      typewriter.typeString('O D I N F I S T')
                        .start();
                    }} options={{
                      cursor: '|',
                    }}></Typewriter>
                  </h1>
                  <h4 className="description">
                    A red-blue-team cyber intrusion simulation system for <span className="text-primary jarv1s " >MIL-1553</span> avionic platforms.</h4>
                  <br />
                </div>
              </div>
              {this.state.slides.length < 1 ? null :
                <div className="col-md-10 ml-auto mr-auto scenes-container" >
                  <Collapse isOpen={this.state.page == 'RUN'}>
                    <Carousel ref={this.scene_selector} slides={this.state.slides} height={500} />
                  </Collapse>
                </div>}
              <div className="col-md-10 ml-auto mr-auto">
                <h3><a href="/scenes" onClick={e => {
                  e.preventDefault();
                  if (this.state.page == 'START')
                    this.setState({ page: 'RUN' })
                  else if (this.state.page == 'RUN') {
                    this.setState({ page: 'LOAD' })
                    console.log(this.scene_selector.current.state)
                    let selected = this.state.scenes[this.scene_selector.current.state.slideCurrent];
                    this.setState({ message: `Loading ${selected.name} ...` })
                    ax.post('/api/run/' + selected.name).then(() => {
                      setTimeout(() => this.props.history.push("/mission"), 1000);
                    })
                  }
                }} className='start-a'>{this.get_message()}</a></h3>
              </div>
            </div>
          </div>

        </div>
      </>
    );
  }
}

export default withRouter(Landing);
