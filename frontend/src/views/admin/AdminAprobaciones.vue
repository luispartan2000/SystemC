<template>
  <div>
    <h1>Gestión de Aprobaciones</h1>

    <div class="card">
      <div v-if="loading" class="loading">Cargando alumnos…</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Matrícula</th>
            <th>Alumno</th>
            <th>Curso</th>
            <th>Nivel</th>
            <th>Aprobado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="insc in inscripciones" :key="insc.id">
            <td>{{ insc.matricula }}</td>
            <td>{{ insc.alumno }}</td>
            <td>{{ insc.curso }}</td>
            <td>{{ insc.nivel }}</td>
            <td>
              <span v-if="insc.aprobado" class="badge success">Sí</span>
              <span v-else class="badge warning">No</span>
            </td>
            <td>
              <button
                v-if="!insc.aprobado"
                class="primary"
                @click="aprobar(insc.id)"
                :disabled="updating"
              >
                ✔ Aprobar
              </button>
              <button
                v-else
                class="danger"
                @click="revocar(insc.id)"
                :disabled="updating"
              >
                ✖ Revocar
              </button>
            </td>
          </tr>
          <tr v-if="!inscripciones.length">
            <td colspan="6" class="muted">No hay inscripciones registradas</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const inscripciones = ref([])
const loading = ref(false)
const updating = ref(false)

const getCookie = (n) =>
  (`; ${document.cookie}`).split(`; ${n}=`).pop()?.split(";")[0] || ""

const cargarInscripciones = async () => {
  loading.value = true
  try {
    const res = await fetch("http://localhost:8000/api/admin/inscripciones/", {
      credentials: "include",
    })
    const data = await res.json()
    if (res.ok) inscripciones.value = data.inscripciones || []
    else inscripciones.value = []
  } catch (e) {
    inscripciones.value = []
  } finally {
    loading.value = false
  }
}

const aprobar = async (id) => {
  updating.value = true
  try {
    await fetch(`http://localhost:8000/api/admin/inscripciones/${id}/aprobar/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      credentials: "include",
    })
    await cargarInscripciones()
  } finally {
    updating.value = false
  }
}

const revocar = async (id) => {
  updating.value = true
  try {
    await fetch(`http://localhost:8000/api/admin/inscripciones/${id}/revocar/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      credentials: "include",
    })
    await cargarInscripciones()
  } finally {
    updating.value = false
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
.badge { padding: .3rem .6rem; border-radius: 6px; font-size: .85rem; font-weight: bold; }
.badge.success { background: #d4edda; color: #155724; }
.badge.warning { background: #fff3cd; color: #856404; }
button.primary { background: #28a745; color: #fff; border: none; padding: .4rem .8rem; border-radius: 6px; cursor: pointer; }
button.danger { background: #c0392b; color: #fff; border: none; padding: .4rem .8rem; border-radius: 6px; cursor: pointer; }
</style>
