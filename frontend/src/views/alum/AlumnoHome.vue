<template>
  <div class="home-wrap">
    <div class="card">
      <h1>Bienvenido al área de alumno</h1>

      <div v-if="error" class="msg error">{{ error }}</div>

      <div v-else>
        <h2 class="subtitle">Tus calificaciones:</h2>

        <ul v-if="calificaciones.length > 0" class="list">
          <li v-for="c in calificaciones" :key="c.id" class="list-item">
            <span class="muted">{{ c.materia }}:</span>
            <b> {{ c.calificacion }} </b>
            <span class="muted"> ({{ c.fecha }})</span>
          </li>
        </ul>

        <p v-else class="muted">No tienes calificaciones aún.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const calificaciones = ref([])
const error = ref('')

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
      if (res.status === 403) router.push('/')
    }
  } catch (err) {
    error.value = 'Error al obtener calificaciones'
    router.push('/')
  }
})
</script>

<style scoped>
.home-wrap{
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.card{
  width: 100%;
  max-width: 860px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
  padding: 1.4rem;
}

h1{ margin: 0 0 .6rem 0; color: #26344a; }
.subtitle{ margin: .2rem 0 .6rem 0; color: #26344a; }


.list{ list-style: none; padding: 0; margin: 0; }
.list-item{ padding: .5rem 0; border-bottom: 1px solid #eee; }
.list-item:last-child{ border-bottom: none; }

.muted{ color: #99a; }


.msg{ margin-top: 1rem; font-weight: bold; text-align: center; }
.error{ color: #e74c3c; }
</style>
