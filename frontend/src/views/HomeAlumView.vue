<template>
  <div class="home-alum-bg">
    <ChangePassButton />
    <LogoutBtn />
    <h1>Bienvenido al área de alumno</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-else>
      <h2>Tus calificaciones:</h2>
      <ul v-if="calificaciones.length > 0">
        <li v-for="c in calificaciones" :key="c.id">
          {{ c.materia }}: <b>{{ c.calificacion }}</b> ({{ c.fecha }})
        </li>
      </ul>
      <p v-else>No tienes calificaciones aún.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ChangePassButton from '../components/ChangePassButton.vue'
import LogoutBtn from '../components/Logout-btn.vue'

const router = useRouter()
const calificaciones = ref([])
const error = ref('')

const logout = async () => {

  localStorage.removeItem('matricula')
  localStorage.removeItem('tipo')
  router.push('/')
}

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/api/alumno/calificaciones/', {
      credentials: 'include' 
    })
    const data = await res.json()
    if (res.ok) {
      calificaciones.value = data.calificaciones
    } else {
      error.value = data.error || 'No se pudieron obtener las calificaciones'
      if (res.status === 403) {
        router.push('/')
      }
    }
  } catch (err) {
    error.value = 'Error al obtener calificaciones'
    router.push('/')
  }
})
</script>

<style scoped>
.home-alum-bg {
  min-height: 100vh;
  background: #e6ebef;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}
h1 {
  color: #222c36;
}
.error {
  color: #e74c3c;
  font-weight: bold;
  margin-top: 1em;
}
</style>
