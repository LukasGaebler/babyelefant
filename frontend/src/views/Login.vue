<template>
  <div id="login">
    <div class="row login-row">
      <div class="col-sm-4"></div>
      <div class="col-sm-4 card login-card">
        <form @submit="login">
          <img
          id="logo"
          src="../assets/BabyElefant_Logo.png"
          width="60px"
          height="51px"
          class="img-fluid"
        />
        <h4>Willkommen bei Babyelefant</h4>
        <h6>Bitte melden Sie sich an, um weiter zur Applikation zu kommen</h6>
        <div class="error" v-if="showUsernameError">Bitte geben Sie einen Username ein</div>
        <input
          class="form-control"
          placeholder="Username"
          type="text"
          v-model="username"
        />
        <div class="error" v-if="showPasswordError">Bitte geben Sie eine Passwort ein</div>
        <input
          class="form-control"
          placeholder="Password"
          type="password"
          id="passwordInput"
          v-model="password"
        />
        <div class="error">{{loginErrorText}}</div>
        <button type="submit" class="btn btn-success" id="submitButton">
          Anmelden
        </button>
        </form>
      </div>
      <div class="col-sm-4"></div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';
import jwt_decode from "jwt-decode";

export default {
  name: "login",
  data() {
    return {
      isauthenticated: true,
      username: "",
      password: "",
      showUsernameError: false,
      showPasswordError: false,
      loginError: false,
      loginErrorText: ''
    };
  },
  components: {},
  methods: {
    authenticateUser() {
      this.isauthenticated = !this.isauthenticated;
    },

    authenticateAdmin() {
      this.isauthenticated = !this.isauthenticated;
    },

    login(e) {
      e.preventDefault();


      var hasError = false;
      if(this.username.length == 0) {
        this.showUsernameError = true
        hasError = true
      } else {
        this.showUsernameError = false
      }
      

      if(this.password.length == 0) {
        this.showPasswordError = true
        hasError = true
      } else {
        this.showPasswordError = false
      }

      if(hasError) { return; }
    


      var obj = {
        username: this.username,
        password: this.password,
      };
      api
        .post(process.env.VUE_APP_API_URL + "/auth/login", obj)
        .then(
          function (data) {
            var token = data.data.token;
            localStorage.setItem("token", token);
            var user = jwt_decode(token);
            localStorage.setItem("user", JSON.stringify(user));
            localStorage.setItem("admin", user.sub.admin);
            // localStorage.setItem("admin", true); //delete Later
            if(user.sub.admin) {
              this.$router.push({name: "dashboard"})
            } else {
              this.$router.push({ name: "dashboard" });
            }
          }.bind(this)
        )
        .catch((err) => {
          this.loginError = false
          if(err.response.status == 401) {
            this.loginErrorText = err.response.data;
          } else {
            this.loginErrorText = "Beim Login ist ein Fehler aufgetreten";
          }
        });
    },
  },
};
</script>

<style>
form {
  width: 100%;
}

#login {
  height: 100vh;
  background-color: #F7F7Ff;
}


.error {
  color: red
}

#app {
  height: 100%;
}

html,
body {
  height: 100%;
  width: 100%;
}

body {
  overflow-x: hidden;
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

/* @media screen and (max-width: 565px) {
  .NavItem {
    font-size: 5vw;
    margin-top: 0;
    margin-left: 10px;
    margin-right: 10px;
  }

  .NavItem:hover {
    font-size: 5vw;
  }

  .custom-col {
    text-align:center;
    align-content: center;
    align-items: center;
  }

  #sidenav-content {
    width: 100%;
  }
}*/ 
</style>