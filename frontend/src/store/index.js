import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

const getters = {
  isAuthenticated: state => !!state.token,
  authStatus: state => state.status,
}

const state = {
  token: localStorage.getItem('token') || '',
  status: '',
}


export default new Vuex.Store({
  state,
  mutations: {},
  actions: {},
  modules: {},
  getters
});
