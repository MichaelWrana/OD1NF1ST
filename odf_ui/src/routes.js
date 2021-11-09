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
import Cyberdeck from "./views/Cyberdeck.jsx";
import axios from 'axios';


var staticRoutes = [
  {
    path: "/cyberdeck",
    name: "Cyberdeck",
    icon: "tim-icons icon-controller",
    component: Cyberdeck,
    layout: "/admin"
  },];

var refRoutes =
  [
    // {
    //   path: "/icons",
    //   name: "Icons",
    //   icon: "tim-icons icon-atom",
    //   component: Icons,
    //   layout: "/admin"
    // },
    // {
    //   path: "/map",
    //   name: "Map",
    //   icon: "tim-icons icon-pin",
    //   component: Map,
    //   layout: "/admin"
    // },
    // {
    //   path: "/notifications",
    //   name: "Notifications",
    //   icon: "tim-icons icon-bell-55",
    //   component: Notifications,
    //   layout: "/admin"
    // },
    // {
    //   path: "/user-profile",
    //   name: "User Profile",
    //   icon: "tim-icons icon-single-02",
    //   component: UserProfile,
    //   layout: "/admin"
    // },
    // {
    //   path: "/tables",
    //   name: "Table List",
    //   icon: "tim-icons icon-puzzle-10",
    //   component: TableList,
    //   layout: "/admin"
    // },
    // {
    //   path: "/typography",
    //   name: "Typography",
    //   icon: "tim-icons icon-align-center",
    //   component: Typography,
    //   layout: "/admin"
    // },
  ];


function fetchRoutes(callback) {
  // axios.get(`/api/portals`)
  //   .then(res => {
  var routes = [];
  //     const portals = res.data;
  //     for (let i = 0; i < portals.length; i++) {
  //       var p = portals[i];
  //       routes.push({
  //         mission: p,
  //         path: '/' + p.mission,
  //         name: p.name,
  //         icon: "tim-icons " + p.icon,
  //         component: MissionPortal,
  //         layout: "/admin"
  //       });
  //     }
  routes = routes.concat(staticRoutes);
  routes = routes.concat(refRoutes);
  //     callback(routes);
  //   })
  callback(routes);
};




export default fetchRoutes
