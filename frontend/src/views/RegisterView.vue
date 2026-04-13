<script setup>
import RegisterForm from '../components/RegisterForm.vue'
</script>

<template>
  <div class="register-bg">
    <RegisterForm />
  </div>
</template>

<style scoped>
.register-bg {
  min-height: 100vh;
  background: #00b5e2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
h1 {
  color: #fafafa;
  font-size: 2.8rem;
  margin-bottom: 2rem;
  letter-spacing: 2px;
  text-shadow: 1px 2px 16px #1e1e1e;
  text-align: center;
}
</style>
