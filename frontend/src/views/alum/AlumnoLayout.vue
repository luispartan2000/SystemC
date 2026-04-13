<template>
  <div class="alumno-layout">
    <aside class="sidebar">
      <div class="brand">
        <img src="/logobuap.svg" alt="Logo BUAP" />
      </div>

      <nav class="nav">
        <button
          :class="{ active: $route.name === 'alum-home' }"
          @click="$router.push({ name: 'alum-home' })"
        >
          Inicio
        </button>

        <button
          :class="{ active: $route.name === 'alum-cursos' }"
          @click="$router.push({ name: 'alum-cursos' })"
        >
          Mis cursos
        </button>

        <button
          :class="{ active: $route.name === 'alum-calificaciones' }"
          @click="$router.push({ name: 'alum-calificaciones' })"
        >
          Calificaciones
        </button>
      </nav>

      <div class="session-actions">
        <LogoutBtn />
        <ChangePassButton />
      </div>
    </aside>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import LogoutBtn from '@/components/Logout-btn.vue'
import ChangePassButton from '@/components/ChangePassButton.vue'
</script>

<style scoped>
.alumno-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: #ecf2f9;
}

.sidebar {
  background: linear-gradient(180deg, #003b5c 0%, #005b8e 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 1.2rem;
  box-shadow: 2px 0 24px #0002;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.2rem;
}
.brand img {
  width: 140px;
  opacity: 0.95;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,.25));
}

.nav {
  display: flex;
  flex-direction: column;
  gap: .5rem;
  margin-top: .4rem;
}
.nav button {
  padding: .75rem 1rem;
  border: none;
  border-radius: 8px;
  text-align: left;
  background: #00466f;
  color: #fff;
  font-weight: 600;
  letter-spacing: .5px;
  cursor: pointer;
  transition: transform .08s, background .15s;
  box-shadow: 0 2px 10px rgba(0,0,0,.12);
}
.nav button:hover { background: #006aa3; transform: translateX(2px); }
.nav button.active { background: #00b5e2; color: #003b5c; }

.session-actions {
  margin-top: auto;
  display: grid;
  gap: .6rem;
}

.content {
  padding: 2rem 2.4rem;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,.08);
  padding: 1.4rem;
}

@media (max-width: 980px) {
  .alumno-layout { grid-template-columns: 1fr; }
  .sidebar { position: sticky; top: 0; z-index: 10; }
}
</style>
