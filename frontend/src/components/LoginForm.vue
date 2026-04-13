<template>
  <div class="login-bg">
    <div class="login-card">
      <img src="/logobuap.svg" alt="Logo" class="logo-img" />
      <form class="login-form" @submit.prevent="login">
        <input v-model="matricula" placeholder="Matrícula" required />
        <input v-model="password" type="password" placeholder="Contraseña" required />
        <button type="submit" class="login-btn">LOGIN</button>
        <RouterLink to="/registro">
          <AppButton class="opt-btn">¿No tienes Cuenta? Regístrate</AppButton>
        </RouterLink>
        <button type="button" class="recovery-btn" @click="router.push('/recuperar-password')">
          ¿Olvidaste tu contraseña?
        </button>
        <div v-if="msg" :class="msgType">{{ msg }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import AppButton from './AppButton.vue'

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const router = useRouter()
const matricula = ref('')
const password = ref('')
const msg = ref('')
const msgType = ref('')

// en la siguiente logica pido siempre el token para poder saber quien esta haciendo el login esto para proceder con mis demas cosas agregue un timeout para poder darle chance a la cookie
const getCSRFToken = async () => {
  await fetch('http://localhost:8000/api/csrf/', { credentials: 'include' });
  await new Promise(r => setTimeout(r, 100));
  return getCookie('csrftoken');
}

const login = async () => {
  msg.value = ''
  msgType.value = ''
  const csrftoken = await getCSRFToken()
  if (!csrftoken) {
    msgType.value = 'error'
    msg.value = 'No se pudo obtener el token CSRF. Intenta recargar la página.'
    return
  }

  try {
    const res = await fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ matricula: matricula.value, password: password.value }),
      credentials: 'include'
    })
    const data = await res.json()
    if (res.ok) {
      if (data.must_change_password) {
        msgType.value = 'warning'
        setTimeout(() => {
          router.push('/cambiar-contrasena')
        }, 1000)
        return
      }
      msgType.value = 'success'
      msg.value = data.success
      if (data.tipo == 'ALUMNO') router.push('/home-alum')
      else if (data.tipo == 'STAF') router.push('/staf')
      else if (data.tipo == 'ADMIN') router.push('/admin-panel')
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
.login-bg {
  min-height: 100vh;
  min-width: 100vw;
  background: linear-gradient(135deg, #003b5c 0%, #00b5e2 60%, #00b5e2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  background: #00b5e2;
  border-radius: 14px;
  box-shadow: 0 4px 40px #0007;
  padding: 2.5rem 2.8rem 2.3rem 2.8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 370px;
}

.logo-img {
  width: 90px;
  height: 90px;
  object-fit: contain;
  border-radius: 50%;
  margin-bottom: 2rem;
  box-shadow: 0 2px 24px #0002;
  background: #fff7;
}

.login-form {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
}

.login-form input {
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

.login-form input:focus {
  box-shadow: 0 2px 18px #007cf730;
}

.login-btn {
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
.login-btn:hover {
  background: #495ba1;
  transform: scale(1.04);
}
.login-btn:active{
  transform: scale(0.97);
}

.opt-btn {
  margin-top: 1.2em;
  background: transparent !important;
  color: #eee !important;
  font-weight: 600;
  font-size: 0.97em;
  border: none;
  border-radius: 5px;
  width: 100%;
  cursor: pointer;
  text-align: center;
  transition: color 0.18s;
}
.opt-btn:hover{
  color: #ffe8d5 !important;
}
.recovery-btn {
  background: none;
  border: none;
  color: #cdd3ea;
  margin-top: 1.1em;
  text-decoration: underline;
  font-size: 0.98em;
  cursor: pointer;
  text-align: right;
  transition: color 0.15s;
}
.recovery-btn:hover {
  color: #ffe7be;
}
.success, .error, .warning {
  margin-top: 1.1em;
  font-weight: bold;
  text-align: center;
}
.success { color: #2ecc71; }
.error { color: #e74c3c; }
.warning { color: #f1c40f; }
</style>
