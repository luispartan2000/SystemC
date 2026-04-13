<template>
  <div class="admin-login-bg">
    <form class="admin-login-form" @submit.prevent="login">
      <h1>Login Admin</h1>
      <input v-model="matricula" placeholder="Matrícula Admin" required />
      <input v-model="password" type="password" placeholder="Contraseña" required />
      <button type="submit">Entrar</button>
      <div v-if="msg" :class="msgType">{{ msg }}</div>
    </form>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const matricula = ref('')
const password = ref('')
const msg = ref('')
const msgType = ref('')

const login = async () => {
  msg.value = ''
  msgType.value = ''
  try {
    const res = await fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ matricula: matricula.value, password: password.value }),
    })
    const data = await res.json()
    if (res.ok && data.tipo === "ADMIN") {
      localStorage.setItem('matricula', matricula.value)
      localStorage.setItem('tipo', data.tipo)
      router.push('/admin-panel')
    } else {
      msgType.value = 'error'
      msg.value = 'Acceso solo para administradores.'
    }
  } catch {
    msgType.value = 'error'
    msg.value = 'Error de conexión'
  }
}
</script>
<style scoped>
.admin-login-bg { min-height: 100vh; background: #002c47; display: flex; align-items: center; justify-content: center; }
.admin-login-form { background: #fff; border-radius: 12px; box-shadow: 0 4px 24px #0004; padding: 2rem 1.5rem; display: flex; flex-direction: column; align-items: center; max-width: 350px;}
.admin-login-form h1 { color: #003b5c;}
.admin-login-form input {margin: 0.4em 0; width: 100%; padding: 0.7em;}
button {padding: .7em 2em; background: #003b5c; color: #fff; border: none; border-radius: 6px;}
.error {margin-top: 1em; color: #e74c3c;}
</style>
