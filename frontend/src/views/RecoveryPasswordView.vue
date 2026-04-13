<template>
  <div class="recovery-bg">
    <form class="recovery-form" @submit.prevent="recuperar">
      <h1>Recuperar Contraseña</h1>
      <input v-model="email" type="email" placeholder="Correo registrado" required :disabled="loading"/>
      <button type="submit" class="recovery-btn" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        <span v-else>Enviar correo de recuperación</span>
      </button>
      <div v-if="msg" :class="msgType">{{ msg }}</div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'

const email = ref('')
const msg = ref('')
const msgType = ref('')
const loading = ref(false)
const router = useRouter()

const recuperar = async () => {
  msg.value = ''
  msgType.value = ''
  loading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/recuperar-password/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })
    const data = await res.json()
    if (res.ok) {
      msg.value = data.success || 'Revisa tu correo electrónico'
      msgType.value = 'success'
      email.value = ''

      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      msg.value = data.error || 'No se pudo enviar el correo'
      msgType.value = 'error'
    }
  } catch (e) {
    msg.value = 'Error de conexión'
    msgType.value = 'error'
  }
  loading.value = false
}
</script>

<style scoped>
.recovery-bg {
  min-height: 100vh;
  background: #e5eefd;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.recovery-form {
  background: #fff;
  padding: 2rem 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 24px #0002;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 350px;
}
input {
  margin: 0.4em 0;
  width: 100%;
  padding: 0.7em;
  border: 1px solid #b1b6e2;
  border-radius: 5px;
  background: #f3f6fd;
  font-size: 1em;
  color: #222c36;
}
.recovery-btn {
  width: 100%;
  padding: 0.7em;
  background: #00b5e2;
  color: #fff;
  font-weight: bold;
  font-size: 1.08em;
  border: none;
  border-radius: 6px;
  margin-top: 1em;
  cursor: pointer;
  box-shadow: 0 2px 10px #5468ff25;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.recovery-btn[disabled] {
  opacity: 0.7;
  cursor: not-allowed;
}
.spinner {
  border: 2px solid #e5eefd;
  border-top: 2px solid #003b5c;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  margin-right: 7px;
  animation: spin 1s linear infinite;
  display: inline-block;
  vertical-align: middle;
}
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
.success { color: #2ecc71; margin-top: 1em; text-align: center; font-weight: bold; }
.error { color: #e74c3c; margin-top: 1em; text-align: center; font-weight: bold; }
</style>
