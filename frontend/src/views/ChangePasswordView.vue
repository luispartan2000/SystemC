<template>
  <div class="change-pw-bg">
    <h1>Cambiar Contraseña</h1>
    <form @submit.prevent="cambiar">
      <input v-model="actual" type="password" placeholder="Contraseña actual" required />
      <input v-model="nueva" type="password" placeholder="Nueva contraseña" required />
      <input v-model="confirmar" type="password" placeholder="Confirmar nueva contraseña" required />
      <button type="submit">Cambiar contraseña</button>
    </form>
    <div v-if="msg" :class="msgType">{{ msg }}</div>
  </div>
</template>

<script setup>
import { useRouter, RouterLink } from 'vue-router'
import { ref } from 'vue'
const router = useRouter()
const actual = ref('')
const nueva = ref('')
const confirmar = ref('')
const msg = ref('')
const msgType = ref('')

const cambiar = async () => {
  msg.value = ''
  msgType.value = ''
  try {
    const res = await window.csrfFetch('http://localhost:8000/api/cambiar-contrasena/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        actual: actual.value,
        nueva: nueva.value,
        confirmar: confirmar.value
      }),
    })
    const data = await res.json()
    if (res.ok) {
      msg.value = data.success
      msgType.value = 'success'
      actual.value = nueva.value = confirmar.value = ''
      setTimeout(()=>{
        router.push('/')
      }, 1500)
    } else {
      msg.value = data.error || 'Error desconocido'
      msgType.value = 'error'
    }
  } catch (e) {
    msg.value = 'Error de conexión'
    msgType.value = 'error'
  }
}
</script>

<style scoped>
.change-pw-bg {
  min-height: 100vh;
  background: #e5eefd;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
form {
  background: #fff;
  padding: 2rem 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 24px #0002;
  display: flex;
  flex-direction: column;
  align-items: center;
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
button {
  width: 100%;
  padding: 0.7em;
  background: #5468ff;
  color: #fff;
  font-weight: bold;
  font-size: 1.08em;
  border: none;
  border-radius: 6px;
  margin-top: 1em;
  cursor: pointer;
  box-shadow: 0 2px 10px #5468ff25;
}
.success { color: #2ecc71; margin-top: 1em; text-align: center; font-weight: bold; }
.error { color: #e74c3c; margin-top: 1em; text-align: center; font-weight: bold; }
</style>
