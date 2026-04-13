<template>
  <div>
    <h1>Supervisión de Inscripciones</h1>

    <div class="card">
      <div v-if="loading" class="loading">Cargando…</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Curso</th>
            <th>Profesor</th>
            <th>Inscritos</th>
            <th>Pagados</th>
            <th>Pendientes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in cursos" :key="c.id">
            <td>{{ c.nombre }} (Nivel {{ c.nivel }})</td>
            <td>{{ c.profesor }}</td>
            <td>{{ c.inscritos }}</td>
            <td>{{ c.pagados }}</td>
            <td>{{ c.pendientes }}</td>
          </tr>
          <tr v-if="!cursos.length">
            <td colspan="5" class="muted">No hay cursos con inscripciones</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const cursos = ref([])
const loading = ref(false)

const cargarInscripciones = async () => {
  loading.value = true
  try {
    const res = await fetch("http://localhost:8000/api/staf/inscripciones/", {
      credentials: "include",
    })
    const data = await res.json()
    if (res.ok) cursos.value = data.cursos || []
    else cursos.value = []
  } catch (e) {
    cursos.value = []
  } finally {
    loading.value = false
  }
}

onMounted(cargarInscripciones)
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
  padding: 1.4rem;
  margin-top: 1rem;
}
.loading { padding: .5rem 0; color: #666; }
.muted { color: #99a; text-align: center; }
.table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.table th, .table td { padding: .6rem .5rem; border-bottom: 1px solid #eee; text-align: left; }
</style>
