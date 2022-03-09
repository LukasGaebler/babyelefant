<template>
<div id="root">
    <h5>Admin / Show Users / User #{{$route.params.id}}</h5>
    <button type="button" id="back-button" class="btn btn-info" v-on:click="returnToShowAllUsers">
        <span class="material-icons">arrow_back</span>
    </button>
    <div class="row" style="margin-top: 1%;">
        <div class="col-sm-7">
            <input id="firstLineInput" v-model="firstLinePass" type="password" placeholder="Neues Passwort" class="form-control" />
            <input id="confirmPass"  style="margin-top: 1%;" v-model="secondLinePass" type="password" placeholder="Neues Passwort bestätigen" class="form-control" />    
            <button style="margin-top: 1%" class="btn btn-success" type="submit" v-bind:disabled="this.firstLinePass !== this.secondLinePass || this.secondLinePass.length == 0 || this.firstLinePass.lenght == 0" v-on:click="pushNewPassword">Confirm new password</button>
        </div>
    </div>
</div>
</template>

<script>
import api from "../services/api"

export default {
    name: "EditUserForm",
    data() {
        return {
            firstLinePass: "",
            secondLinePass: "",
            isSame: true,
        };
    },
    components: {
        
    },
    mounted() {
        this.checkIfSamePassword
    },
    methods: {
        pushNewPassword() {
            api.put(process.env.VUE_APP_API_URL +  "/users/" + this.$route.params.id, {u_pwd: this.secondLinePass});
        },

        checkIfSamePassword() {
            this.isSame = true;
        },

        returnToShowAllUsers() {
            this.$router.back({name: "showAllUsers"})
        }
    }
}
</script>

<style scoped>
#form {
  margin-top: 20px;
}

#back-button {
  display: flex;
  padding: 5px;
}
</style>