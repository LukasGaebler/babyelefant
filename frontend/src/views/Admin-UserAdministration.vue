<template>
    <div>
        <h5>Admin / Show Users</h5>
        <div id="allUsers">
            <AllUsers />
        </div>
    </div>
</template>

<script>
import AllUsers from "../components/Admin-ListUsers";


export default {
    name: "showUsers",
    components: {
        AllUsers
    }
}
</script>

<style scoped>


</style>
