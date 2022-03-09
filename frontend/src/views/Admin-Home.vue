<template>
  <div id="mainAdmin" class="main">
    <Sidebar />
    <div class="maincontent">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import Sidebar from "../components/SidebarAdmin";

export default {
  name: "Admin",
  components: {
    Sidebar,
  },
  mounted() {},
  methods: {},
};
</script>

<style scoped>
.maincontent {
  margin-left: 280px;
  padding-top: 10px;
  padding-left: 10px;
  height: 100%;
}

.main {height: 100%;
  background-color: #F5F6FB;

}
</style>