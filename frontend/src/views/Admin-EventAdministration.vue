<template>
  <div class="main">
      <div id="content">
          <select class="form-control" v-model="selectedUser" @change="loadEvents()">
            <option v-for="user in users" :key="user.u_id" v-bind:value="user.u_id">{{ user.u_name }}</option>
        </select>
        <button class="btn btn-success" v-on:click="addEvent()" style="margin-top: 1%; width: 100%;">Add event</button>
        <div v-if="events.length != 0">
            <div v-for="eventCollection in events" :key="eventCollection.id">
            <div class="row" style="margin-top: 1%">
                <div class="col-sm-6" v-for="event in eventCollection.data" :key="event.e_id">
                    <div class="card custom-card">
                        <h3>{{ event.e_name }}</h3>
                        <div class="row">
                            <div class="col-sm-6">
                                <button class="btn btn-info" style="width: 100%" v-on:click="addCamera(event.e_id)">Add camera</button>
                            </div>
                            <div class="col-sm-6">
                                <button class="btn btn-danger" style="width: 100%" v-on:click="showRemoveableCameras(event.e_id)">Remove camera</button>
                            </div>
                        </div>
                    </div>
                </div>  
            </div>
            <div class="row" style="margin-top: 1%;" v-if="removeCamera == eventCollection.data[0].e_id || (eventCollection.data[1] != undefined  && removeCamera == eventCollection.data[1].e_id)">
                <div class="col-sm-12">
                    <div class="card custom-card">
                        <div v-if="removeableCameras.length != 0">
                            <div v-for="collection in removeableCameras" :key="collection.id">
                                <div class="row" style="margin-top: .5%">
                                    <div class="col-sm-6" v-for="cam in collection.data" :key="cam.c_id">
                                        <div class="card custom-card">
                                            <h5>ID: {{ cam.c_id }}</h5>
                                            <h5>Link: {{ cam.c_link }}</h5>
                                            <div class="row">
                                                <div class="col-sm-6">
                                                    <button class="btn btn-danger" v-on:click="deleteCamera(cam.c_id)">Delte camera</button>
                                                </div>
                                            </div>
                                        </div>
                                        
                                    </div>
                                </div>
                            </div>
                        </div>
                        <button class="btn btn-info" style="margin-top: 1%" v-on:click="closeRemove()">Close</button>
                    </div>
                </div>
            </div>
        </div>
        </div>
      </div>
  </div>
</template>

<script>
import api from "../services/api"

export default {
    name: "AdminEvents",
    data() {
        return {
            users: [],
            events: [],
            selectedUser: undefined,
            removeCamera: -1,
            removeableCameras: []
        }
    }, 
    mounted() {
        this.loadUsers();
    },
    methods: {
        async loadUsers() {
            var res = await api.get(process.env.VUE_APP_API_URL + "/users/");
            this.users = res.data.data;
            this.selectedUser = this.users[0].u_id;
            this.loadEvents();
        },
        loadEvents() {
            // TODO: On select of user, load the events from this user,
            // and display them
            this.events = [];
            api.get(process.env.VUE_APP_API_URL + "/admin/events/" + this.selectedUser).then((data) => {
                var arrays = [], size = 2, i = Math.floor(Math.random() * 10000) + 1;
                while (data.data.data.length > 0) {
                    arrays.push({id: i, data: data.data.data.splice(0, size)})
                    i = Math.floor(Math.random() * 10000) + 1;
                }
                this.events = arrays;
            });
        },
        addCamera(event) {
            var ip = prompt("Please enter the ip address / hostname", "http://192.168.1.10");
            var maxDist = prompt("Please enter the max distance in m", "2 for 2 meters");
            var startDowntime = prompt("Downtime start (24 hour format)", "20:00");
            var endDowntime = prompt("Downtime end (24 hour format)", "06:00");
            api.post(process.env.VUE_APP_API_URL + "/cameras/", {
                c_link: ip,
                c_e_event: event,
                c_maxdistance: maxDist,
                c_start: startDowntime,
                c_end: endDowntime
            }).then(() => {
                alert("camera was added");
            });
        },
        showRemoveableCameras(eventid) {
            this.removeCamera = eventid;
            api.get(process.env.VUE_APP_API_URL + "/cameras/" + eventid).then((data) => {
                var arrays = [], size = 2, i = Math.floor(Math.random() * 10000) + 1;
                while (data.data.cameras.length > 0) {
                    arrays.push({id: i, data: data.data.cameras.splice(0,size)});
                    i = Math.floor(Math.random() * 10000) + 1;    
                }
                this.removeableCameras = arrays;   
            })
        },
        closeRemove() {
            this.removeCamera = -1;
        },
        deleteCamera(cam) {
            api.delete(process.env.VUE_APP_API_URL + "/cameras/" + cam).then(() => {
                this.showRemoveableCameras(this.removeCamera);
            });
        },
        addEvent() {
            var name = prompt("Name of the event", "test event");
            var adress = prompt("Adress of the event", "");
            api.post(process.env.VUE_APP_API_URL + "/events/" ,{
                e_name: name,
                e_u_user: this.selectedUser,
                e_adress: adress
            }).then(() => {
                this.loadEvents();
            });
            
        }
    }
}
</script>

<style>

#content {
    margin-right: 2%;
}

.custom-card {
    padding: 10px;
}
</style>