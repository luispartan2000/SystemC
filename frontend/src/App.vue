<script setup>
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'


const route = useRoute()
const showNavbar = !['/registro', '/homealum', '/hometeach'].includes(route.path)

</script>

<template>
<!--   <NavBar /> -->
  <router-view />
</template>


<style scoped>
body {
  margin: 0;
  padding: 0;
}
</style>
