<template>
  <div id="root">
    <div class="row">
      <div class="col-sm-10"></div>
      <div class="col-sm-2">
        <button
          v-if="!isEvent"
          v-on:click="swapScreens()"
          class="btn btn-info"
          style="width: 100%"
        >
          Eventdashboard
        </button>
        <button
          v-if="isEvent"
          v-on:click="swapScreens()"
          class="btn btn-info"
          style="width: 100%"
        >
          Camera Dashboard
        </button>
      </div>
    </div>
    <CameraStatsList v-if="!isEvent" class="data" />
    <EventStatsList
      v-if="isEvent"
      class="data"
      v-bind:eventId="this.$route.params.eventId"
    />
  </div>
</template>

<script>
/* import api from '../services/api'; */
import CameraStatsList from "../components/CameraStatsList";
import EventStatsList from "../components/EventStats";

export default {
  name: "Camera",
  data: function() {
    return {
      streams: [],
      isEvent: false,
    };
  },
  components: {
    CameraStatsList,
    EventStatsList,
  },
  mounted() {},
  watch: {
    "$route.params.eventId"() {
      this.clear();
    },
  },
  methods: {
    clear() {
      this.streams = [];
    },
    swapScreens() {
      this.isEvent = !this.isEvent;
    },
  },
};
</script>

<style scoped>
.head {
  display: flex;
  align-content: center;
  align-items: center;
  justify-content: space-between;
  /* margin: 10px 15px 10px 15px; */
}

.row {
  margin: 5px 2px 5px 2px;
}

#root {
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-right: 2%;
}

img {
  display: block;
  place-self: center;
  max-width: 560px;
  height: 315px;
  border-radius: 10px;
}

h2 {
  color: darkblue;
}

.dataContent {
  margin: 5px;
  padding: 10px;
  background-color: white;
  border-radius: 10px;
  text-align: center;
}

h4 {
  color: grey;
  font-size: 18px;
}

.dataContent h3 {
  color: black;
}

.graph {
  background-color: white;
  border-radius: 10px;
  padding: 10px;
  margin: 5px;
}

.streamsList {
  display: flex;
  flex-direction: column;
}

/*.btn {
  background-color: #AFEEEE;
  box-shadow: 0 2.8px 2.2px rgba(0, 0, 0, 0.034),
  0 6.7px 5.3px rgba(0, 0, 0, 0.048);
  font-size: 18px;
  font-weight: 500;
  color: #05386B;
}*/
</style>
