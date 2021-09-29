<template>
  <div id="Events">
    <h2>Events</h2>
    <table class="table table-striped table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Eventname</th>
          <th scope="col">Addresse</th>
          <th scope="col" colspan="2" style="text-align: center">Optionen</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ev in events" :key="ev.e_id">
          <td>{{ ev.e_name }}</td>
          <td>{{ ev.e_adress ? ev.e_adress : "Nicht angegeben" }}</td>
          <td>
            <button class="btn btn-danger" @click="deleteEvent(ev.e_id)">
              Delete
            </button>
          </td>
          <td>
            <button
              class="btn btn-primary"
              @click="editEvent(ev.e_id, ev.e_name, ev.e_adress)"
            >
              Edit
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from "../services/api";
import Vue from "vue";
import VueToast from "vue-toast-notification";
import "vue-toast-notification/dist/theme-default.css";

export default {
  name: "EventTable",
  data() {
    return {
      events: [],
    };
  },
  mounted() {
    this.init();
    this.loadEvents();
  },
  methods: {
    init() {
      this.$root.$on("reloadEventTable", () => {
        this.loadEvents();
      });
    },
    loadEvents() {
      api.get(process.env.VUE_APP_API_URL + "/getAllEvents").then((data) => {
        this.events = data.data.Event_List;
      });
    },
    deleteEvent(id) {
      api
        .delete(process.env.VUE_APP_API_URL + "/deleteEvent/" + id)
        .then(() => {
          this.loadEvents();
          Vue.use(VueToast);
          Vue.$toast.open({
            message: "Das Event wurde erfolgreich entfernt",
            position: "top-right",
          });
        });
    },
    editEvent(id, name, adress) {
      this.$root.$emit("editEvent", { id: id, name: name, adress: adress });
    },
  },
};
</script>

<style scoped>
#Events {
  box-shadow: 0 1px 2px grey;
  margin: 5px;
  padding: 10px;
  border-radius: 10px;
}

.btn {
  width: 100%;
}
</style>
