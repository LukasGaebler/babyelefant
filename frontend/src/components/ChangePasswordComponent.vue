<template>
  <div id="main">
    <div class="col-sm-6">
      <h4>Passwort ändern</h4>
      <input id="firstLineInput" v-model="firstLinePass" type="password" placeholder="Neues Passwort" class="form-control" />
      <input id="confirmPass" v-model="secondLinePass" type="password" placeholder="Neues Passwort bestätigen" class="form-control" />
      <input class="btn btn-dark" type="submit" value="Passwort ändern" v-on:click="changePass" v-bind:disabled="this.firstLinePass !== this.secondLinePass || this.firstLinePass === '' "/>
    </div>
  </div>
</template>

<script>
import api from "../services/api"
export default {
  name: "ChangePasswordForms",
  data() {
    return {
      firstLinePass: "",
      secondLinePass: ""
    };
  },
  components: {},
  methods: {
    changePass() {
      var user = JSON.parse(localStorage.getItem("user"));
      api.put(process.env.VUE_APP_API_URL + "/user/changePwd/" + user.identity.user_id, {u_pwd: this.secondLinePass});
    }
  }
};
</script>

<style scoped>
.inputField {
  font-weight: 600;
  font-size: 23px;
  padding: 11px;
  border-radius: 10px;
  box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.38);
  border: transparent 1px;
  width: 50%;
  margin: 10px 0px 0px 0px;
}
#inputgroup {
  display: flex;
  flex-direction: column;
}
#changePassword {
  padding: 20px 0px 20px 20px;
  border-radius: 10px;
}
#confirmPass,
.btn-success {
  margin-top: 1%;
}
h4 {
  color: black;
}
</style>