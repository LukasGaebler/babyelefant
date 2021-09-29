<template>
  <div class="sidenav">
    <div class="head">
      <div id="logo">
        <img id="image" src="../assets/BabyElefant_Logo_White_with_circle.png" />
        <h3>Babyelephant</h3>
      </div>
      <span class="material-icons menu btn" v-on:click="extendMenu()">menu</span>
    </div>
    <div id="content" v-bind:class="{contentHide:isExtended}">
      <p>Home</p>
      <div id="homeContent" class="ItemsGroup">
        <button
          class="btn navButton shadow-none"
          v-on:click="$router.push({ name: 'dashboard' })"
        >
          <div class="item">
            <span class="material-icons">leaderboard</span>
            <p><span class="navText">Dashboard</span></p>
          </div>
        </button>
      </div>
      <p>Events</p>
      <div id="homeContent" class="ItemsGroup">
        <div v-for="event in events" :key="event.e_id">
          <button
            type="button"
            class="btn navButton shadow-none"
            v-on:click="
              $router.push({ name: 'camera', params: { eventId: event.e_id } })
            "
          >
            <div class="item">
              <span class="material-icons">event</span>
              <p>
                <span class="navText">{{ event.e_name }}</span>
              </p>
            </div>
          </button>
        </div>
      </div>
      <!--<p>Dateien</p>
    <div id="homeContent" class="ItemsGroup">
      <button type="button" class="btn navButton shadow-none" v-on:click="goToCamera()">
        <div class="item">
          <span class="material-icons">description</span>
          <p><span class="navText">Zusammenfassungen</span></p>
        </div>
      </button>
      <button type="button" class="btn navButton shadow-none" v-on:click="goToStats()">
        <div class="item">
          <span class="material-icons">6_ft_apart</span>
          <p><span class="navText">Daten der Abstandsmessung</span></p>
        </div>
      </button>
      <button type="button" class="btn navButton shadow-none" v-on:click="goToStats()">
        <div class="item">
          <span class="material-icons">masks</span>
          <p><span class="navText">Daten der Maskenerkennung</span></p>
        </div>
      </button>
    </div>-->
      <p>Aktionen</p>
      <button class="btn navButton shadow-none" v-on:click="logout()">
        <div class="item">
          <span class="material-icons">logout</span>
          <p><span class="navText">Abmelden</span></p>
        </div>
      </button>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  name: "sidebar",
  data() {
    return {
      events: [],
      isExtended: false,
    };
  },
  mounted() {
    this.loadEvents();
  },
  methods: {
    goToCamera() {
      this.$router.push({ name: "camera" });
    },

    goToStats() {
      this.$router.push({ name: "statistics" });
    },
    loadEvents() {
      try {
        api.get(process.env.VUE_APP_API_URL + "/events/").then((data) => {
          var events = data.data.data;
          events.forEach((element) => {
            this.events.push(element);
          });
        });
      } catch (err) {
        console.log(err);
      }
    },
    logout() {
      localStorage.clear();
      this.$router.push({ name: "login" });
    },
    extendMenu() {
      this.isExtended = !this.isExtended;
    }
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
    padding: 10px 0px 10px 0px;
  }

  .menu, .btn {
    width: auto;
    height: auto;
    margin: 0px;
    padding: 0px;
  }

  .contentHide {
    display: none;    
  }

  .head {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    margin-right: 0.5rem;
  }

  .menu {
    display: inline-block;
    font-size: 8vw;
    
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
    border-right:1px solid lightgray;
  }

  .menu {
    display: none;
  }
}
</style>
