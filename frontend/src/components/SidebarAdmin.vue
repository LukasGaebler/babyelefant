<template>
  <div class="sidenav">
    <div id="logo">
      <img id="image" src="../assets/BabyElefant_Logo_White_with_circle.png" />
      <h3>Babyelephant</h3>
    </div>
    <div id="content">
      <p>Home</p>
      <div id="homeContent" class="ItemsGroup">
        <button
          class="btn navButton shadow-none"
          v-on:click="$router.push({ name: 'showUsers' })"
        >
          <div class="item">
            <span class="material-icons">people</span>
            <p><span class="navText">Users</span></p>
          </div>
        </button>
        <button
          class="btn navButton shadow-none"
          v-on:click="$router.push({ name: 'adminEvents' })"
        >
          <div class="item">
            <span class="material-icons">event</span>
            <p><span class="navText">Events</span></p>
          </div>
        </button>
        <button class="btn navButton shadow-none" v-on:click="logout()">
          <div class="item">
            <span class="material-icons">logout</span>
            <p><span class="navText">Logout</span></p>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "sidebar-admin",
  data() {
    return {
      events: [],
    };
  },
  methods: {
    goToCamera() {
      this.$router.push({ name: "camera" });
    },

    goToStats() {
      this.$router.push({ name: "statistics" });
    },
    logout() {
      localStorage.clear();
      this.$router.push({ name: "login" });
    },
  },
};
</script>

<style scoped>
#logo {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.ItemsGroup {
  display: flex;
  flex-direction: column;
}

#image {
  max-width: 65px;
  height: 65px;
  display: block;
  margin-left: 1rem;
  margin-right: 10px;
}

#content {
  margin-left: 1rem;
  color: black;
}

.item {
  display: flex;
  flex-direction: row;
  padding: 3px;
  font-size: 1rem;
  align-items: center;
  fill: gray;
  justify-content: flex-start;
}

.navText {
  color: rgb(82, 82, 82);
  margin-left: 1rem;
}

.navButton {
  border: none;
  margin-right: 15px;
  outline: 0;
}

.navButton:hover {
  color: white;
  background-color: white;
}

.navButton:hover .item {
  background-color: #457b9d;
  color: white;
}

.navButton:hover .navText {
  color: white;
}

.navButton:hover .material-icons {
  color: white;
}

.item {
  background-color: white;
  border: none;
}

.material-icons {
  color: rgb(82, 82, 82);
  margin-right: 5px;
}

.btn p {
  padding: 0px;
  margin: 0px;
  top: 0px;
  color: blue;
  font-size: 16px;
}

.btn {
  padding: 0px;
  margin: 0px;
  width: 100%;
}

p {
  color: purple;
  margin-top: 5%;
  margin-bottom: 0px;
  font-size: 0.9rem;
  color: darkgray;
}

@media only screen and (max-width: 600px) {
  .sidenav {
    width: 100%;
    height: auto;
    background-color: white;
  }
}
@media only screen and (min-width: 600px) {
  .sidenav {
    width: 280px;
    display: flex;
    height: 100%;
    position: fixed;
    flex-direction: column;
    z-index: 1;
    top: 0;
    left: 0;
    background-color: white;
    padding-top: 20px;
  }
}
</style>
