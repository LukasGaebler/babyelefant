<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
import Vue from "vue";
import VueToast from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-default.css';

export default {
  data: function () {
    return {};
  },
  mounted() {
    this.attachConnectivityListeners();
  },
  methods: {
    attachConnectivityListeners() {
      window.addEventListener("offline", function () {
        Vue.use(VueToast);
        Vue.$toast.open({
          message: "Keine Internetverbindung!",
          type: "error",
        });
      });

      window.addEventListener("online", function () {
        
        Vue.use(VueToast);
        Vue.$toast.open({
          message: "Sie sind wieder online! Die Seite wird neugeladen...",
          type: "info",
        });
        

      }).then(() => this.$router.go(0));
    },
  },
};
</script>

<style>
#app {
  height: 100vw;
  padding: 0px;
  margin: 0px;
  overflow-x: visible;
}

html,
body {
  padding: 0px;
  margin: 0px;
  height: 100%;
  overflow-x: visible;
  background-color: #f7f7ff; /* Not it */
  font-family: "Open Sans", sans-serif;
}

.login-card {
  text-align: center;
  padding: 10px;
  align-items: center;
}

.login-row {
  margin: 10%;
}

#passwordInput,
#submitButton {
  margin-top: 1%;
}

#submitButton {
  width: 100%;
}
</style>
