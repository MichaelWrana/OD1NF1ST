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
import { Route, Switch } from "react-router-dom";
// javascript plugin used to create scrollbars on windows
import PerfectScrollbar from "perfect-scrollbar";

// core components
import AdminNavbar from "../../components/Navbars/AdminNavbar.jsx";
import Footer from "../../components/Footer/Footer.jsx";
import Sidebar from "../../components/Sidebar/Sidebar.jsx";
import FixedPlugin from "../../components/FixedPlugin/FixedPlugin.jsx";

import fetchRoutes from "../../routes.js";

import logo from "../../assets/img/react-logo.png";

var ps;

class Admin extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      theme: "blue",
      sidebarOpened:
        document.documentElement.className.indexOf("nav-open") !== -1,
      sidebarMinimized:
        document.documentElement.className.indexOf("sidebar-mini") !== -1,
      routes: [],
    };
  }
  componentDidMount() {
    document.documentElement.className += " sidebar-mini";
    if (navigator.platform.indexOf("Win") > -1) {
      document.documentElement.className += " perfect-scrollbar-on";
      document.documentElement.classList.remove("perfect-scrollbar-off");
      ps = new PerfectScrollbar(this.refs.mainPanel, { suppressScrollX: true });
      let tables = document.querySelectorAll(".table-responsive");
      for (let i = 0; i < tables.length; i++) {
        ps = new PerfectScrollbar(tables[i]);
      }
    }
    fetchRoutes(routes => {
      this.setState({ routes: routes });
    });
  }
  componentWillUnmount() {
    if (navigator.platform.indexOf("Win") > -1) {
      ps.destroy();
      document.documentElement.className += " perfect-scrollbar-off";
      document.documentElement.classList.remove("perfect-scrollbar-on");
    }
  }
  componentDidUpdate(e) {
    if (e.history.action === "PUSH") {
      if (navigator.platform.indexOf("Win") > -1) {
        let tables = document.querySelectorAll(".table-responsive");
        for (let i = 0; i < tables.length; i++) {
          ps = new PerfectScrollbar(tables[i]);
        }
      }
      document.documentElement.scrollTop = 0;
      document.scrollingElement.scrollTop = 0;
      this.refs.mainPanel.scrollTop = 0;
    }
  }
  // this function opens and closes the sidebar on small devices
  toggleSidebar = () => {
    document.documentElement.classList.toggle("nav-open");
    this.setState({ sidebarOpened: !this.state.sidebarOpened });
  };
  minimizeSideBar = () => {
    document.documentElement.classList.toggle("sidebar-mini");
    this.setState({ sidebarMinimized: !this.state.sidebarMinimized });
  };
  getRoutes = routes => {
    return routes.map((prop, key) => {
      if (prop.layout === "/admin") {
        return (
          <Route
            path={prop.layout + prop.path}
            component={() => React.createElement(prop.component, {
              ...this.state,
              mission: prop.mission, key: key
            })}
            key={key}
          />
        );
      } else {
        return null;
      }
    });
  };
  handleBgClick = color => {
    this.setState({ theme: color });
  };
  getBrandText = path => {
    for (let i = 0; i < this.state.routes.length; i++) {
      if (
        this.props.location.pathname.indexOf(
          this.state.routes[i].layout + this.state.routes[i].path
        ) !== -1
      ) {
        return this.state.routes[i].name;
      }
    }
    return "Brand";
  };
  render() {
    return (
      <>
        <div className="wrapper">
          <Sidebar
            {...this.props}
            routes={this.state.routes}
            bgColor={this.state.theme}
            logo={{
              text: "J . A . R . V . 1 . S",
              imgSrc: logo
            }}
            toggleSidebar={this.toggleSidebar}
          />
          <div
            className="main-panel"
            ref="mainPanel"
            data={this.state.theme}
          >
            <AdminNavbar
              {...this.props}
              brandText={this.getBrandText(this.props.location.pathname)}
              toggleSidebar={this.toggleSidebar}
              sidebarOpened={this.state.sidebarOpened}
            />
            <Switch>{this.getRoutes(this.state.routes)}</Switch>
            {// we don't want the Footer to be rendered on map page
              this.props.location.pathname.indexOf("maps") !== -1 ? null : (
                <Footer fluid />
              )}
          </div>
        </div>
        <FixedPlugin
          bgColor={this.state.backgroundColor}
          handleBgClick={this.handleBgClick}
          toggleSidebar={this.minimizeSideBar}
        />
      </>
    );
  }
}

export default Admin;
