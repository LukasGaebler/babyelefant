<template>
  <div class= "root">
    <Sidebar />
    <div class="content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import Sidebar from '../components/Sidebar' 

export default {
  name: "UserDashboard",
  data() {
    return {
      windowWidth: 0,
    } 
  },
  components: {
    Sidebar
  },
  mounted(){
    
  },
  methods: {
  }
}
</script>

<style scoped>
.root {
  height: 100%;
  background-color: #F7F7FF;

}

.content {
  margin-left: 280px;
  padding-top: 10px;
  padding-left: 10px;
  padding-right: 10px;
  height: 100%;
}

@media only screen and (max-width: 600px) {
  .content {
    margin-left: 0px;
  }
}

</style>
