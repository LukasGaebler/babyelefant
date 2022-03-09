<template>
  <div class="root">
    <div class="streamsList" v-if="streamsLoaded">
      <div class="row" v-for="stream in streams" :key="stream.key">
        <div class="col-sm-6">
          <div class="imagecont">
            <img
              class="StreamImg"
              v-bind:src="stream.streamLink"
            />
            <!-- div class="overlay">
              <button
                class="btn btn-primary"
                v-on:click="calibrate(stream.c_id)"
              >
                Kalibrieren
              </button>
            </!-->
          </div>
        </div>

        <div class="col-sm-6 card">
          <chart
            :apiData="stream.cameraData"
            :key="rerender"
            typeOfData="abstand"
          />
        </div>
      </div>
    </div>
    <br />
  </div>
</template>

<script>
import api from "../services/api";
import chart from "../components/Chart";

export default {
  data: function() {
    return {
      streams: [],
      rerender: 1,
      streamsLoaded: false,
    };
  },
  components: {
    chart,
  },
  mounted() {
    this.getStreams();
  },
  watch: {
    "$route.params.eventId"() {
      this.clear();
      this.getStreams();
    },
  },
  methods: {
    clear() {
      this.streams = [];
    },
    async getStreams() {
      var key = 1;
      await api
        .get(
          process.env.VUE_APP_API_URL + "/cameras/" + this.$route.params.eventId
        )
        .then((data) => {
          data.data.cameras.forEach((element) => {
              var random = Math.floor(Math.random() * Math.pow(2, 31));
              var streamId = element.c_id;
              element.streamLink =
                process.env.VUE_APP_API_URL +
                "/video_feed/" +
                streamId +
                "?i=" +
                random +
                "&jwt=" +
                localStorage.getItem("token");
              element.key = key;
              key++;
              api
                .get(
                  process.env.VUE_APP_API_URL +
                    "/distanceData/camera/" +
                    element.c_id
                )
                .then((data) => {
                  element.cameraData = [
                    [], //Labels X-Achse
                    [], // Average
                    [], // Minimum
                    []
                  ];
                  var stats = data.data.data;
                  var index = stats.length - 50;
                  for (index; index < stats.length; index++) {
                    if (stats[index] != undefined) {
                      element.cameraData[0].push(stats[index]["d_datetime"]);
                      element.cameraData[1].push(stats[index]["d_avg"]);
                      element.cameraData[2].push(stats[index]["d_min"]);
                      element.cameraData[3].push(stats[index]["d_maskedpeople"] / stats[index]["d_numberofpeople"] * 100);
                    }
                  }
                });
              element.loadedGraph = false;
              this.streams.push(element);
            });
            this.streamsLoaded = true;
          setInterval(() => {
            this.streams.forEach((element) => {
              var random = Math.floor(Math.random() * Math.pow(2, 31));
              var streamId = element.c_id;
              element.streamLink =
                process.env.VUE_APP_API_URL +
                "/video_feed/" +
                streamId +
                "?i=" +
                random +
                "&jwt=" +
                localStorage.getItem("token");
              api
                .get(
                  process.env.VUE_APP_API_URL +
                    "/distanceData/camera/" +
                    element.c_id
                )
                .then((data) => {
                  element.cameraData = [
                    [], //Labels X-Achse
                    [], // Average
                    [], // Minimum
                    []
                  ];
                  var stats = data.data.data;
                  var index = stats.length - 50;
                  for (index; index < stats.length; index++) {
                    if (stats[index] != undefined) {
                      element.cameraData[0].push(stats[index]["d_datetime"]);
                      element.cameraData[1].push(stats[index]["d_avg"]);
                      element.cameraData[2].push(stats[index]["d_min"]);
                      element.cameraData[3].push(stats[index]["d_maskedpeople"] / stats[index]["d_numberofpeople"] * 100);
                    }
                  }
                });
                this.forceRerender();
              //element.loadedGraph = false;
            });
          },1000);
          
          //this.streams.push(...data.data.cameras);
          
        });
    },
    loadStream(id) {
      this.streams.forEach((element) => {
        if (element.c_id === id) {
          var random = Math.floor(Math.random() * Math.pow(2, 31));
          element.streamLink =
            process.env.VUE_APP_API_URL +
            "/video_feed/" +
            id +
            "?i=" +
            random +
            "&jwt=" +
            localStorage.getItem("token");
        }

        if (
          element.cameraData != undefined &&
          element.cameraData[0].length > 0 &&
          element.loadedGraph === false
        ) {
          this.forceRerender();
          element.loadedGraph = true;
        }
      });
    },
    forceRerender() {
      this.rerender += 1;
    },
    /*calibrate(id) {
      var x = confirm(
        "Sind Sie sicher, dass Sie diese Kamera kalibrieren wollen?"
      );
      if (x) {
        var dist = prompt(
          "Bitte geben Sie die Distanz ein, wie weit die Menschen entfernt sind. (in Meter)",
          ""
        );
        api
          .post(process.env.VUE_APP_API_URL + "/cameras/" + id, {
            distance: dist,
          })
          .then(() => {
            console.log("calibrated");
          });
      }
    },*/
  },
};
</script>

<style scoped>
.StreamImg {
  max-width: 100%;
  max-height: 100%;
  border-radius: 5px;
}

.row {
  margin-top: 1rem;
}

h4 {
  color: grey;
}

.dataContent h3 {
  color: black;
}

.card-custom {
  background-color: white;
  height: 100%;
}

.overlay {
  position: absolute;
  bottom: 0;
  transition: 0.5s ease;
  opacity: 0;
  text-align: center;
  padding: 10px;
}

.imagecont:hover .overlay {
  opacity: 1;
}
</style>