import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import api from "./services/api";
import "bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'


api.interceptors.request.use(
  config => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.common["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

Vue.config.productionTip = false;




new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
