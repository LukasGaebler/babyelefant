<template>
    <div id="addEventComponent">
        <div>
            <h5>Neues Event anlegen</h5>
            <div class="error" v-if="eventNameError">Bitte geben Sie einen Namen für das Event an</div>
            <form @submit="addEvent">
                <input class="form-control" type="text" placeholder="Name des Events (erforderlich)" v-model="eventName" />
            <input class="form-control" type="text" placeholder="Adresss des Events (optional)" id="eventAdress" v-model="eventAdress" />
            <button class="btn btn-success" id="submitButton" type="submit">Event hinzufügen</button>
            </form>
        </div>
    </div>
</template>

<script>
import api from '../services/api'
import Vue from 'vue';
import VueToast from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-default.css';

export default {
    name: 'addEvent',
    data () {
        return {
            eventName: '',
            eventAdress: '',
            eventNameError: false
        }
    },
    methods: {
        addEvent(e) {
            e.preventDefault();
            if(this.eventName.length == 0) {
                this.eventNameError = true
                return
            } else {
                this.eventNameError = false
            }

            var obj = {
                "e_name": this.eventName,
                "e_adress": this.eventAdress.length > 0 ? this.eventAdress : null,
                "e_u_user": JSON.parse(localStorage.getItem("user")).identity.user_id
            }

            api.post(process.env.VUE_APP_API_URL + "/addEvent", obj)
            .then(() => {
                this.$root.$emit("reloadEventTable", "some data");
                Vue.use(VueToast);
                Vue.$toast.open({
                    message: "Das Event wurde erfolgreich hinzugefügt",
                    position: 'top-right',
                });
            })
            .catch((err) => {
                console.log(err)
            })
        }
    },
}
</script>

<style>
#eventAdress, #submitButton {
  margin-top: 1%;
}

#addEventComponent {
box-shadow: 0 1px 2px grey;
margin: 5px;
padding: 10px;
border-radius: 10px;
}
</style>