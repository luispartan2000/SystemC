<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="brand">
        <img src="/logobuap.svg" alt="Logo BUAP" />
      </div>
      <nav class="nav">
        <button :class="{active: seccion==='stafs'}" @click="go('stafs')">Gestionar stafs</button>
        <button :class="{active: seccion==='vouchers'}" @click="go('vouchers')">Validar Vouchers de Pago</button>
        <button :class="{active: seccion==='cursos'}" @click="go('cursos')">Abrir/Cerrar Cursos</button>
        <button :class="{active: seccion==='certificados'}" @click="go('certificados')">Gestionar Certificados</button>
        <button :class="{active: seccion==='inscripciones'}" @click="go('inscripciones')">Inscripciones y Aprobaciones</button>
      </nav>
      <div class="session-actions">
        <LogoutBtn />
        <ChangePassButton />
      </div>
    </aside>

    <main class="content">
      <div v-if="!seccion" class="staf-home">
        <img src="/logobuap.svg" alt="Logo BUAP" class="logo" />
      </div>

      <div v-else-if="seccion==='stafs'">
        <h1>Alta de Usuarios (STAF / ADMIN)</h1>

        <form @submit.prevent="registrarUsuario" class="card form">
          <div class="grid">
            <input v-model="nuevo.matricula" placeholder="Matrícula" required />
            <input v-model="nuevo.first_name" placeholder="Nombre(s)" required />
            <input v-model="nuevo.last_name" placeholder="Apellido(s)" required />
            <input v-model="nuevo.email" placeholder="Correo" type="email" required />

            <div class="field">
              <label>Tipo de usuario</label>
              <select v-model="nuevo.tipo">
                <option value="STAF">STAF</option>
                <option value="ADMIN">ADMIN</option>
              </select>
            </div>

            <div class="field inline">
              <input id="activo" type="checkbox" v-model="nuevo.activo" />
              <label for="activo">Activo</label>
            </div>
          </div>

          <button type="submit" class="primary">Registrar</button>
          <div v-if="msg" :class="msgType" class="msg">{{ msg }}</div>
        </form>

        <!-- Listas -->
        <div class="lists">
          <div class="card">
            <h2>Usuarios STAF / ADMIN</h2>
            <div v-if="loading" class="loading">Cargando…</div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Matrícula</th><th>Nombre</th><th>Correo</th><th>Tipo</th><th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in staff" :key="u.matricula">
                  <td>{{ u.matricula }}</td>
                  <td>{{ u.nombre }}</td>
                  <td>{{ u.email }}</td>
                  <td>{{ u.tipo }} <span v-if="u.is_superuser" class="badge">superuser</span></td>
                  <td>
                    <button class="danger" @click="eliminar(u.matricula)" :disabled="deleting">{{ deleting ? '...' : 'Eliminar' }}</button>
                  </td>
                </tr>
                <tr v-if="!staff.length"><td colspan="5" class="muted">Sin registros</td></tr>
              </tbody>
            </table>
          </div>

          <div class="card">
            <h2>Alumnos</h2>
            <div v-if="loading" class="loading">Cargando…</div>
            <table v-else class="table">
              <thead>
                <tr>
                  <th>Matrícula</th><th>Nombre</th><th>Correo</th><th>Activo</th><th>Área</th><th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in alumnos" :key="a.matricula">
                  <td>{{ a.matricula }}</td>
                  <td>{{ a.nombre }}</td>
                  <td>{{ a.email }}</td>
                  <td>{{ a.activo ? 'Sí' : 'No' }}</td>
                  <td>{{ a.area || '—' }}</td>
                  <td>
                    <button class="danger" @click="eliminar(a.matricula)" :disabled="deleting">{{ deleting ? '...' : 'Eliminar' }}</button>
                  </td>
                </tr>
                <tr v-if="!alumnos.length"><td colspan="6" class="muted">Sin registros</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-else-if="seccion==='vouchers'">
        <h1>Vouchers de Pago</h1>
        <div class="card">Próximamente…</div>
      </div>

      <div v-else-if="seccion==='cursos'">
        <h1>Gestión de Cursos</h1>
        <div class="card">Próximamente…</div>
      </div>

      <div v-else-if="seccion==='certificados'">
        <h1>Gestión de Certificados</h1>
        <div class="card">Próximamente…</div>
      </div>

      <div v-else-if="seccion==='inscripciones'">
        <h1>Inscripciones y Aprobaciones</h1>
        <div class="card">Próximamente…</div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LogoutBtn from '../components/Logout-btn.vue'
import ChangePassButton from '../components/ChangePassButton.vue'

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

const seccion = ref('')
const staff = ref([])
const alumnos = ref([])
const loading = ref(false)
const deleting = ref(false)

const nuevo = ref({
  matricula: '',
  first_name: '',
  last_name: '',
  email: '',
  tipo: 'STAF',
  activo: true
})

const msg = ref('')
const msgType = ref('')

const getCSRFToken = async () => {
  await fetch('http://localhost:8000/api/csrf/', { credentials: 'include' })
  await new Promise(r => setTimeout(r, 100))
  return getCookie('csrftoken')
}

const go = async (sec) => {
  seccion.value = sec
  if (sec === 'stafs') await cargarListas()
}

const cargarListas = async () => {
  loading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/admin/users/', { credentials: 'include' })
    const data = await res.json()
    if (res.ok) {
      staff.value = data.staff || []
      alumnos.value = data.alumnos || []
    } else {
      staff.value = []
      alumnos.value = []
    }
  } catch (e) {
    staff.value = []
    alumnos.value = []
  } finally {
    loading.value = false
  }
}

const registrarUsuario = async () => {
  msg.value = ''; msgType.value = ''
  const csrftoken = await getCSRFToken()
  if (!csrftoken) {
    msgType.value = 'error'
    msg.value = 'No se pudo obtener el token CSRF.'
    return
  }
  try {
    const res = await fetch('http://localhost:8000/api/admin/create-user/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
      credentials: 'include',
      body: JSON.stringify({
        matricula: nuevo.value.matricula,
        first_name: nuevo.value.first_name,
        last_name: nuevo.value.last_name,
        email: nuevo.value.email,
        tipo: nuevo.value.tipo
      })
    })
    const data = await res.json()
    if (res.ok) {
      msgType.value = 'success'
      msg.value = data.success || 'Usuario creado y activado.'
      Object.assign(nuevo.value, { matricula: '', first_name: '', last_name: '', email: '', tipo: 'STAF', activo: true })
      await cargarListas()
    } else {
      msgType.value = 'error'
      msg.value = data.error || 'Error desconocido'
    }
  } catch (e) {
    msgType.value = 'error'
    msg.value = 'Error de conexión'
  }
}

const eliminar = async (matricula) => {
  if (!confirm(`¿Eliminar la cuenta con matrícula ${matricula}? Esta acción es permanente.`)) return
  deleting.value = true
  const csrftoken = await getCSRFToken()
  try {
    const res = await fetch('http://localhost:8000/api/admin/delete-user/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
      credentials: 'include',
      body: JSON.stringify({ matricula })
    })
    const data = await res.json()
    if (res.ok) {
      msgType.value = 'success'
      msg.value = data.success || 'Usuario eliminado.'
      await cargarListas()
    } else {
      msgType.value = 'error'
      msg.value = data.error || 'No se pudo eliminar.'
    }
  } catch (e) {
    msgType.value = 'error'
    msg.value = 'Error de conexión'
  } finally {
    deleting.value = false
  }
}

if (seccion.value === 'stafs') cargarListas()
</script>

<style scoped>
.admin-layout { display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; background: #ecf2f9; }
.sidebar { background: linear-gradient(180deg, #003b5c 0%, #005b8e 100%); color: #fff; display: flex; flex-direction: column; padding: 1.2rem; box-shadow: 2px 0 24px #0002; }
.brand { display: flex; align-items: center; justify-content: center; margin-bottom: 1.2rem; }
.brand img { width: 140px; opacity: 0.95; filter: drop-shadow(0 4px 12px rgba(0,0,0,.25)); }
.nav { display: flex; flex-direction: column; gap: .5rem; margin-top: .4rem; }
.nav button { padding: .75rem 1rem; border: none; border-radius: 8px; text-align: left; background: #00466f; color: #fff; font-weight: 600; letter-spacing: .5px; cursor: pointer; transition: transform .08s, background .15s; box-shadow: 0 2px 10px rgba(0,0,0,.12); }
.nav button:hover { background: #006aa3; transform: translateX(2px); }
.nav button.active { background: #00b5e2; color: #003b5c; }
.session-actions { margin-top: auto; display: grid; gap: .6rem; }
.content { padding: 2rem 2.4rem; }
.card { background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,.08); padding: 1.4rem; }
.form .grid { display: grid; grid-template-columns: repeat(2, minmax(220px, 1fr)); gap: .9rem; }
input, select { margin: 0; padding: .9rem 1rem; border: none; border-radius: 8px; background: #f7f8fa; color: #26344a; font-size: 1rem; box-shadow: 0 2px 10px #0001; outline: none; transition: box-shadow .18s; width: 100%; }
input:focus, select:focus { box-shadow: 0 2px 18px #007cf730; }
.field { display: flex; flex-direction: column; gap: .35rem; }
.field.inline { flex-direction: row; align-items: center; gap: .6rem; }
.field label { font-weight: 700; font-size: .94rem; color: #003b5c; }
button.primary { margin-top: 1rem; padding: .95rem 1.1rem; border: none; border-radius: 8px; background: #26344a; color: #fff; font-weight: 800; letter-spacing: 1.2px; font-size: 1.05rem; cursor: pointer; box-shadow: 0 2px 14px #203d5a30; transition: background .16s, transform .09s; }
button.primary:hover { background: #495ba1; transform: scale(1.03); }
button.primary:active { transform: scale(.98); }
.msg { margin-top: 1rem; font-weight: bold; text-align: center; }
.success { color: #2ecc71; }
.error { color: #e74c3c; }
.loading { padding: .5rem 0; color: #666; }
.muted { color: #99a; text-align: center; }
.badge { margin-left: .4rem; font-size: .8rem; padding: .15rem .4rem; border-radius: 6px; background: #eef2ff; color: #334; }
.table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.table th, .table td { padding: .6rem .5rem; border-bottom: 1px solid #eee; text-align: left; }
button.danger { background: #c0392b; color: #fff; border: none; border-radius: 6px; padding: .4rem .7rem; cursor: pointer; }
button.danger:disabled { opacity: .6; cursor: not-allowed; }
.lists { display: grid; grid-template-columns: 1fr; gap: 1rem; margin-top: 1.2rem; }
.staf-home { display: flex; align-items: center; justify-content: center; height: calc(100vh - 4rem); }
.logo { max-width: 300px; opacity: 0.9; }
@media (max-width: 980px) {
  .admin-layout { grid-template-columns: 1fr; }
  .sidebar { position: sticky; top: 0; z-index: 10; }
  .form .grid { grid-template-columns: 1fr; }
}
</style>
