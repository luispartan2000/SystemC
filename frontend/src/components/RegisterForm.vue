<template>
  <div class="register-bg">
    <div class="register-container">
      <h1 style="color:white">Registro</h1>
      <form @submit.prevent="register">
        <input v-model="matricula" placeholder="Matrícula" required />
        <input v-model="first_name" placeholder="Nombre(s)" required />
        <input v-model="last_name" placeholder="Apellido(s)" required />
        <input v-model="email" type="email" placeholder="Correo" required />
        <input v-model="telefono" placeholder="Teléfono" />
        <input v-model="area" placeholder="Área" />
        <label class="file-upload">
          <span>Subir identificación</span>
          <input type="file" @change="onFileChange" />
        </label>
        <span v-if="fileName">{{ fileName }}</span>


        <input v-model="password" type="password" placeholder="Contraseña" required />
        <button type="submit">Registrarse</button>
      </form>
      <div v-if="msg" :class="msgType">{{ msg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'


const router = useRouter()
const matricula = ref('')
const first_name = ref('')
const last_name = ref('')
const email = ref('')
const telefono = ref('')
const password = ref('')
const area = ref('')
const activo = ref(true)
const identidad = ref(null)

const msg = ref('')
const msgType = ref('')

const onFileChange = (e) => {
  const files = e.target.files
  identidad.value = files && files[0] ? files[0] : null
}

const register = async () => {
  msg.value = ''
  msgType.value = ''
  try {
    const form = new FormData()
    form.append('matricula', matricula.value)
    form.append('first_name', first_name.value)
    form.append('last_name', last_name.value)
    form.append('email', email.value)
    form.append('telefono', telefono.value)
    form.append('password', password.value)
    form.append('area', area.value || '')
    form.append('activo', activo.value ? 'true' : 'false')
    if (identidad.value) {
      form.append('identidad', identidad.value)
    }

    const res = await fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      // Importante: NO establecer manualmente Content-Type con multipart
      body: form,
    })

    const data = await res.json()
    if (res.ok) {
      msgType.value = 'success'
      msg.value = data.success
      setTimeout(() => {
        matricula.value = ''
        first_name.value = ''
        last_name.value = ''
        email.value = ''
        telefono.value = ''
        password.value = ''
        area.value = ''
        activo.value = true
        identidad.value = null
        router.push('/')
      }, 1200)
    } else {
      msgType.value = 'error'
      msg.value = data.error || 'Error desconocido'
    }
  } catch (error) {
    msgType.value = 'error'
    msg.value = 'Error de conexión'
  }
}

</script>

<style scoped>
.register-bg {
  min-height: 100vh;
  min-width: 100vw;
  background: linear-gradient(135deg, #003b5c 0%, #00b5e2 60%, #00b5e2 100%) !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-container {
  background: #00b5e2;
  border-radius: 14px;
  box-shadow: 0 4px 40px #0007;
  padding: 2.5rem 2.8rem 2.3rem 2.8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 370px;
}

h1 {
  color: #fff;
  font-size: 2rem;
  margin-bottom: 1.6rem;
  letter-spacing: 2px;
  text-shadow: 0 2px 12px #0004;
  text-align: center;
}

.register-container form {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
}

.register-container input {
  margin: 0.5em 0;
  padding: 1em 1.1em;
  border: none;
  border-radius: 5px;
  background: #f7f8fa;
  color: #26344a;
  font-size: 1.07em;
  box-shadow: 0 2px 10px #0001;
  outline: none;
  transition: box-shadow 0.18s;
}

.register-container input:focus {
  box-shadow: 0 2px 18px #007cf730;
}

.register-container button {
  margin-top: 1.1em;
  padding: 1em;
  border: none;
  border-radius: 5px;
  background: #26344a;
  color: #fff;
  font-weight: 700;
  letter-spacing: 2px;
  font-size: 1.12em;
  cursor: pointer;
  box-shadow: 0 2px 14px #203d5a30;
  transition: background 0.16s, transform 0.09s;
}
.register-container button:hover {
  background: #495ba1;
  transform: scale(1.04);
}
.register-container button:active {
  transform: scale(0.97);
}

.success, .error, .warning {
  margin-top: 1.1em;
  font-weight: bold;
  text-align: center;
}
.success { color: #2ecc71; }
.error { color: #e74c3c; }
.warning { color: #f1c40f; }

.file-upload {
  display: inline-block;
  padding: 10px 20px;
  background-color: #26344a; /* azul bonito */
  color: white;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.file-upload:hover {
  background: #495ba1;
  transform: scale(1.04);
}

.file-upload input[type="file"] {
  display: none; /* ocultamos el feo input */
}

</style>

