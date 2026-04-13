<template>
    <button class="logout-btn" @click="handleLogout">
        Cerrar Sesión
    </button>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter()

const handleLogout = async () => {
  try {
    console.log('Cerrando sesión...');
    const res = await window.csrfFetch('http://localhost:8000/api/logout/', {
      method: 'POST'
    });
    if (!res.ok) {
      const data = await res.json();
      console.error('Error al cerrar sesión:', data);
    }
  } catch (err) {
    console.error('Error en logout:', err);
  }
  localStorage.removeItem('matricula');
  localStorage.removeItem('tipo');
  router.push('/');
};
</script>

<style scoped>
.logout-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  padding: 1em 2em;
  border: none;
  border-radius: 5px;
  background: #66899d;
  color: #fff;
  font-weight: 700;
  letter-spacing: 2px;
  font-size: 0.9em;
  cursor: pointer;
  box-shadow: 0 2px 14px #203d5a30;
  transition: background 0.16s, transform 0.09s;
}
.logout-btn:hover {
  background:  #495ba1;
  transform: scale(1.04);
}
.logout-btn:active {
  transform: scale(0.97);
}
</style>
