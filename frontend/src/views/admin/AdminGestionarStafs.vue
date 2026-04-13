<template>
  <div>
    <h1>Alta de Usuarios (STAFF / ADMIN)</h1>

    <form @submit.prevent="registrarUsuario" class="card form">
      <div class="grid">
        <input v-model="nuevo.matricula" placeholder="Matrícula" required />
        <input v-model="nuevo.first_name" placeholder="Nombre(s)" required />
        <input v-model="nuevo.last_name" placeholder="Apellido(s)" required />
        <input v-model="nuevo.email" placeholder="Correo" type="email" required />

        <div class="field">
          <label>Tipo de usuario</label>
          <select v-model="nuevo.tipo">
            <option value="STAF">STAFF</option>
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

    <div class="lists">
      <div class="card">
        <h2>Usuarios STAFF / ADMIN</h2>
        <div v-if="loading" class="loading">Cargando…</div>
        <table v-else class="table">
          <thead>
            <tr><th>Matrícula</th><th>Nombre</th><th>Correo</th><th>Tipo</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in staff" :key="u.matricula">
              <td>{{ u.matricula }}</td>
              <td>{{ u.nombre }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.tipo }} <span v-if="u.is_superuser" class="badge">superuser</span></td>
              <td><button class="danger" @click="eliminar(u.matricula)" :disabled="deleting">{{ deleting ? '...' : 'Eliminar' }}</button></td>
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
            <tr><th>Matrícula</th><th>Nombre</th><th>Correo</th><th>Activo</th><th>Área</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            <tr v-for="a in alumnos" :key="a.matricula">
              <td>{{ a.matricula }}</td>
              <td>{{ a.nombre }}</td>
              <td>{{ a.email }}</td>
              <td>{{ a.activo ? 'Sí' : 'No' }}</td>
              <td>{{ a.area || '—' }}</td>
              <td><button class="danger" @click="eliminar(a.matricula)" :disabled="deleting">{{ deleting ? '...' : 'Eliminar' }}</button></td>
            </tr>
            <tr v-if="!alumnos.length"><td colspan="6" class="muted">Sin registros</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

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

const getCookie = (n) => (`; ${document.cookie}`).split(`; ${n}=`).pop()?.split(';')[0] || ''

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
    staff.value = []; alumnos.value = []
  } finally { loading.value = false }
}

const registrarUsuario = async () => {
  msg.value = ''; msgType.value = ''
  try {
    const res = await fetch('http://localhost:8000/api/admin/create-user/', {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'X-CSRFToken': getCookie('csrftoken') },
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
      Object.assign(nuevo.value, { matricula:'', first_name:'', last_name:'', email:'', tipo:'STAF', activo:true })
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
  try {
    const res = await fetch('http://localhost:8000/api/admin/delete-user/', {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'X-CSRFToken': getCookie('csrftoken') },
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

onMounted(cargarListas)
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
  padding: 1.4rem;
  margin-top: 1rem;
}
.form .grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: .9rem;
}
input, select {
  margin: 0;
  padding: .9rem 1rem;
  border: none;
  border-radius: 8px;
  background: #f7f8fa;
  color: #26344a;
  font-size: 1rem;
  box-shadow: 0 2px 10px #0001;
  outline: none;
  transition: box-shadow .18s;
  width: 100%;
}
input:focus, select:focus { box-shadow: 0 2px 18px #007cf730; }
.field { display: flex; flex-direction: column; gap: .35rem; }
.field.inline { flex-direction: row; align-items: center; gap: .6rem; }
.field label { font-weight: 700; font-size: .94rem; color: #003b5c; }
button.primary {
  margin-top: 1rem;
  padding: .95rem 1.1rem;
  border: none;
  border-radius: 8px;
  background: #26344a;
  color: #fff;
  font-weight: 800;
  letter-spacing: 1.2px;
  font-size: 1.05rem;
  cursor: pointer;
  box-shadow: 0 2px 14px #203d5a30;
  transition: background .16s, transform .09s;
}
button.primary:hover { background: #495ba1; transform: scale(1.03); }
button.primary:active { transform: scale(.98); }

.loading { padding: .5rem 0; color: #666; }
.muted { color: #99a; text-align: center; }
.badge { margin-left: .4rem; font-size: .8rem; padding: .15rem .4rem; border-radius: 6px; background: #eef2ff; color: #334; }
.table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.table th, .table td { padding: .6rem .5rem; border-bottom: 1px solid #eee; text-align: left; }
button.danger { background: #c0392b; color: #fff; border: none; border-radius: 6px; padding: .4rem .7rem; cursor: pointer; }
button.danger:disabled { opacity: .6; cursor: not-allowed; }

@media (max-width: 980px) {
  .form .grid { grid-template-columns: 1fr; }
}
</style>
