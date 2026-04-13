<template>
  <div class="home-staf-bg">
    <h1>Bienvenido al área de staf</h1>
    <LogoutBtn />
    <p>Aquí podrás gestionar la validación de alumnos.</p>

    <div v-if="authLoading" class="info">Verificando permisos...</div>
    <div v-else-if="!isStaf" class="error">
      No tienes permisos para ver esta sección. Inicia sesión como staf.
    </div>

    <section v-else style="margin-top:2rem; width:100%; max-width:900px;">
      <h2>Alumnos en espera de validación</h2>

      <div v-if="loading" class="info">Cargando...</div>
      <div v-else-if="error" class="error">{{ error }}</div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Matrícula</th>
            <th>Nombre</th>
            <th>Área</th>
            <th>Documento</th>
            <th style="width:120px;"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="alumnos.length === 0">
            <td colspan="5" style="text-align:center; padding:1rem;">No hay alumnos en espera.</td>
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
                @click="validar(a.id)"
                :disabled="validandoId===a.id"
                class="btn"
                title="Validar alumno"
              >
                {{ validandoId===a.id ? 'Validando...' : 'Validar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="msg" :class="msgType" style="margin-top:1rem;">{{ msg }}</div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LogoutBtn from '../components/Logout-btn.vue'

const alumnos = ref([])
const loading = ref(false)
const error = ref('')
const msg = ref('')
const msgType = ref('')
const validandoId = ref(null)

const authLoading = ref(true)
const isStaf = ref(false)

const ensureCsrf = async () => {
  try { await fetch('http://localhost:8000/api/csrf/', { credentials: 'include' }) } catch {}
}
const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return ''
}

const checkWhoAmI = async () => {
  authLoading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/whoami/', {
      credentials: 'include',
    })
    if (!res.ok) { isStaf.value = false; return }
    const data = await res.json()
    isStaf.value = data.tipo === 'STAF' 
  } catch {
    isStaf.value = false
  } finally {
    authLoading.value = false
  }
}

const fetchPendientes = async () => {
  if (!isStaf.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('http://localhost:8000/api/staf/alumnos-pendientes/', {
      credentials: 'include',
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Error al cargar pendientes')
    alumnos.value = data.alumnos || []
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
    const csrftoken = getCookie('csrftoken') || ''
    const res = await fetch('http://localhost:8000/api/staf/validar-alumno/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({ alumno_id }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'No se pudo validar')
    msgType.value = 'success'
    msg.value = data.success
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
.home-staf-bg {
  min-height: 100vh;
  background: #fff7e6;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
}
h1 { color: #a65c0c; }
h2 { margin-bottom: .6rem; color: #a65c0c; }
.info { color: #444; }
.error { color: #e74c3c; font-weight: bold; }
.success { color: #2ecc71; font-weight: bold; }
.tabla {
  width: 100%;
  background: white;
  border-collapse: collapse;
  box-shadow: 0 2px 10px #0001;
  border-radius: 6px;
  overflow: hidden;
}
.tabla th, .tabla td {
  border: 1px solid #eee;
  padding: .7rem .9rem;
  text-align: left;
  vertical-align: middle;
}
.tabla th { background: #fff0d9; font-weight: 700; }
.btn {
  width: 100%;
  padding: .5rem .8rem;
  background: #00a86b;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
