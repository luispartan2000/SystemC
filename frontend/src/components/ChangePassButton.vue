<template>
    <button class="changepass-btn" @click="goToChangePass">
        Cambiar contraseña
    </button>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const goToChangePass = () => {
  router.push('/cambiar-contrasena')
}
</script>

<style scoped>
.changepass-btn {
  position: absolute;
  top: 24px;
  right: 210px;
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
.changepass-btn:hover {
  background:  #495ba1;
  transform: scale(1.04);
}
.changepass-btn:active {
  transform: scale(0.97);
}
</style>
