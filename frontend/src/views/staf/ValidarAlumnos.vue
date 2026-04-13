<template>
  <div>
    <h1>Alumnos en espera de validación</h1>
    <p class="muted">Aquí podrás gestionar la validación de alumnos.</p>

    <div v-if="authLoading" class="loading">Verificando permisos...</div>
    <div v-else-if="!isStaf" class="error">No tienes permisos para ver esta sección.</div>

    <div v-else>
      <div class="card">
        <div v-if="loading" class="loading">Cargando…</div>
        <div v-else-if="error" class="error">{{ error }}</div>

        <table v-else class="table">
          <thead>
            <tr>
              <th>Matrícula</th>
              <th>Nombre</th>
              <th>Área</th>
              <th>Documento</th>
              <th style="width:160px;"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="alumnos.length === 0">
              <td colspan="5" class="muted" style="text-align:center; padding:1rem;">
                No hay alumnos en espera.
              </td>
            </tr>
            <tr v-for="a in alumnos" :key="a.id">
              <td>{{ a.matricula }}</td>
              <td>{{ a.nombre }}</td>
              <td>{{ a.area || '—' }}</td>
              <td>
                <a v-if="a.identidad_url" :href="a.identidad_url" target="_blank" rel="noopener">Ver documento</a>
                <span v-else>—</span>
              </td>
              <td>
                <button
                  class="primary"
                  :disabled="validandoId===a.id"
                  @click="validar(a.id)"
                >
                  {{ validandoId===a.id ? 'Validando...' : 'Validar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="msg" :class="['msg', msgType]">{{ msg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const alumnos = ref([])
const loading = ref(false)
const error = ref('')
const msg = ref('')
const msgType = ref('')
const validandoId = ref(null)
const authLoading = ref(true)
const isStaf = ref(false)

const ensureCsrf = async () => {
  try {
    await fetch('http://localhost:8000/api/csrf/', { credentials: 'include' })
  } catch {}
}
const getCookie = (n) => (`; ${document.cookie}`).split(`; ${n}=`).pop()?.split(';')[0] || ''

const checkWhoAmI = async () => {
  authLoading.value = true
  try {
    const r = await fetch('http://localhost:8000/api/whoami/', { credentials:'include' })
    if (!r.ok) { isStaf.value = false; return }
    const d = await r.json()
    isStaf.value = d.tipo === 'STAF'
  } finally {
    authLoading.value = false
  }
}

const fetchPendientes = async () => {
  if (!isStaf.value) return
  loading.value = true
  error.value = ''
  try {
    const r = await fetch('http://localhost:8000/api/staf/alumnos-pendientes/', { credentials:'include' })
    const d = await r.json()
    if (!r.ok) throw new Error(d.error || 'Error al cargar pendientes')
    alumnos.value = d.alumnos || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const validar = async (alumno_id) => {
  msg.value = ''
  msgType.value = ''
  validandoId.value = alumno_id
  try {
    const r = await fetch('http://localhost:8000/api/staf/validar-alumno/', {
      method:'POST',
      credentials:'include',
      headers:{
        'Content-Type':'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ alumno_id })
    })
    const d = await r.json()
    if (!r.ok) throw new Error(d.error || 'No se pudo validar')
    msgType.value = 'success'
    msg.value = d.success
    await fetchPendientes()
  } catch (e) {
    msgType.value = 'error'
    msg.value = e.message
  } finally {
    validandoId.value = null
  }
}

onMounted(async () => {
  await ensureCsrf()
  await checkWhoAmI()
  await fetchPendientes()
})
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
  padding: 1.4rem;
  margin-top: 1rem;
}

.table { width: 100%; border-collapse: collapse; margin-top: .4rem; }
.table th, .table td { padding: .6rem .7rem; border-bottom: 1px solid #eee; text-align: left; }
.table thead th { background: #eef6ff; }

button.primary {
  padding: .5rem .9rem;
  border: none;
  border-radius: 8px;
  background: #26344a;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 14px #203d5a30;
  transition: background .16s, transform .09s;
}
button.primary:hover { background: #495ba1; transform: translateY(-1px); }
button.primary:disabled { opacity: .6; cursor: not-allowed; }

.loading { color: #666; padding: .4rem 0; }
.muted { color: #99a; }
.msg { margin-top: 1rem; font-weight: bold; text-align: center; }
.success { color: #2ecc71; }
.error { color: #e74c3c; }
</style>
