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
import ReactDOM from "react-dom";
import { createBrowserHistory } from "history";
import { Router, Route, Switch, Redirect } from "react-router-dom";
import AdminLayout from "./layouts/Admin/Admin.jsx";
import Landing from "./layouts/Admin/Landing.jsx";
import Mission from "./views/Mission.jsx";

import "./assets/scss/black-dashboard-react.scss";
import "./assets/demo/demo.css";
import "./assets/css/custom.css";
import "./assets/css/nucleo-icons.css";

const hist = createBrowserHistory();
//Determines what page is rendered from a URL path
//Landing is homepage
ReactDOM.render(
  <Router history={hist}>
    <Switch>
      <Route path="/admin" render={props => <AdminLayout {...props} />} />
      <Route path="/landing" render={props => <Landing {...props} />} />
      <Route path="/mission" render={props => <Mission {...props} />} />
      <Redirect from="/" to="/landing" />
    </Switch>
  </Router>,
  document.getElementById("root")
);
