<template>
    <div id="editEventComponent">
        <div>
            <h5>Event bearbeiten</h5>
            <input class="form-control" type="text" placeholder="Neuer Name des Events (erforderlich)" v-model="newName" />
            <input class="form-control" type="text" placeholder="Neue Adresse des Events (optional)" id="eventAdress" v-model="newAdress" />
            <button class="btn btn-success" id="submitButton" :disabled="buttonDisabled" @click="updateEvent">Event aktualisieren</button>
        </div>
    </div>
</template>

<script>
import api from '../services/api';
import Vue from 'vue';
import VueToast from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-default.css';

export default {
    name: 'editEvent',
    data() {
        return {
            buttonDisabled: true,
            newName: '',
            newAdress: '',
            eventid: -1
        }
    },
    mounted() {
        this.listenForEdit();
    },
    methods: {
        listenForEdit() {
            this.$root.$on("editEvent", (data) => {
                this.buttonDisabled = false
                this.eventid = data.id
                this.newName = data.name
                this.newAdress = data.adress == null ? "" : data.adress
            })
        },
        updateEvent() {
            var obj = {
                "e_name": this.newName,
                "e_adress": this.newAdress
            };

            api.put(process.env.VUE_APP_API_URL + "/event/changeEvent/" + this.eventid, obj)
            .then(() => {
                Vue.use(VueToast);
                Vue.$toast.open({
                    message: "Das Event wurde erfolgreich aktualisiert",
                    position: 'top-right',
                });
                this.$root.$emit("reloadEventTable")
            })
            .catch(() => {
                Vue.use(VueToast);
                Vue.$toast.open({
                    message: "There was an error updating the event",
                    position: 'top-right',
                    type: 'error'
                });
            })
        }
    }
}
</script>

<style>
#eventAdress, #submitButton {
  margin-top: 1%;
}

#editEventComponent {
box-shadow: 0 1px 2px grey;
margin: 5px;
padding: 10px;
border-radius: 10px;
}
</style>