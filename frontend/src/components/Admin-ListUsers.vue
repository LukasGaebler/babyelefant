<template>
<div id="root">
    <button class="btn btn-success" v-on:click="addUser()">User hinzufügen</button>
    <div class="row" v-for="usergroup in users" :key="usergroup.id">
        <div class="col-sm-4" v-for="user in usergroup.data" :key="user.id">
            <div class="card custom-card">
                <h5 class="card-title">{{user.u_name}}</h5>
                <h6 class="card-subtitle mb-2 text-muted">#{{user.u_id}}</h6>
                <p class="card-text">Is Admin: {{user.u_isadmin}}</p>
                <button v-bind:id="user.u_id" class="btn btn-danger" v-on:click= "deleteUser(user.u_id)">Remove</button>
                <button v-bind:id="user.u_id" class="btn btn-success" v-on:click="editUser(user.u_id)">Change Password</button>
            </div>
        </div>
    </div>
</div>
</template>

<script>
import api from "../services/api";

export default {
    name: "AllUsers",
     data() {
        return {
            users: []
        }
    },
    mounted() {
        this.getAllUsers()
    },
    methods: {
        async getAllUsers() {
            var res = await api.get(process.env.VUE_APP_API_URL + "/users/");
            var arrays = [], size = 3, i = Math.floor(Math.random() * 10000) + 1;
            res.data.data = res.data.data.sort((a,b) => (a.u_id > b.u_id) ? 1 : ((b.u_id > a.u_id) ? -1 : 0))
            while (res.data.data.length > 0) {
                arrays.push({id: i, data: res.data.data.splice(0, size)});
                i = Math.floor(Math.random() * 10000) + 1
            }
            this.users = arrays;            
        },
        deleteUser(id) {
            console.log("Removing " + id + "...");
            api.delete(process.env.VUE_APP_API_URL + "/users/" + id).then(() => {
                this.getAllUsers();
            });
        },
        editUser(id) {
            this.$router.push({name: "editUser", params: {id: id}})
        },
        addUser() {
            var username = prompt("Please enter the username", "Test");
            var password = prompt("Please enter the password", "not password");
            api.post(process.env.VUE_APP_API_URL + "/users/", {
                u_name: username,
                u_pwd: password
            }).then(() => {
                this.getAllUsers();
            });
        }
    }
}
</script>

<style scoped>
.card {
    margin: 5px;
}

button {
    margin-right: 10px;    
}

.custom-card {
    padding: 15px;
}

.btn-success {
    margin-top: 1%;
}
</style>