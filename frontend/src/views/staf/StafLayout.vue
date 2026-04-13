<template>
  <div class="staf-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="brand">
        <img src="/logobuap.svg" alt="Logo BUAP" />
      </div>

      <nav class="nav">
        <RouterLink
          :to="{ name: 'staf-home' }"
          class="nav-btn"
          :class="{ active: $route.name === 'staf-home' }"
          replace
        >
          Inicio
        </RouterLink>

        <RouterLink
          :to="{ name: 'staf-validar' }"
          class="nav-btn"
          :class="{ active: $route.name === 'staf-validar' }"
          replace
        >
          Validar alumnos
        </RouterLink>

        <RouterLink
          :to="{ name: 'staf-vouchers' }"
          class="nav-btn"
          :class="{ active: $route.name === 'staf-vouchers' }"
          replace
        >
          Revisar pagos
        </RouterLink>

        <RouterLink
          :to="{ name: 'staf-inscripciones' }"
          class="nav-btn"
          :class="{ active: $route.name === 'staf-inscripciones' }"
          replace
        >
          Supervisión inscripciones
        </RouterLink>
      </nav>

    
      <div class="session-actions">
        <LogoutBtn />
        <ChangePassButton />
      </div>
    </aside>

  
    <main class="content">
      <router-view v-slot="{ Component }">
        <component :is="Component" v-if="Component" />
        <div v-else class="staf-home">
          <img src="/logobuap.svg" alt="Logo BUAP" class="logo" />
        </div>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import LogoutBtn from '@/components/Logout-btn.vue'
import ChangePassButton from '@/components/ChangePassButton.vue'
</script>

<style scoped>
.staf-layout {
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
.nav-btn {
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
  text-decoration: none;
  display: block;
}
.nav-btn:hover { background: #006aa3; transform: translateX(2px); }
.nav-btn.active { background: #00b5e2; color: #003b5c; }

.session-actions { margin-top: auto; display: grid; gap: .6rem; }
.content { padding: 2rem 2.4rem; }

.staf-home { display: flex; align-items: center; justify-content: center; height: calc(100vh - 4rem); }
.logo { max-width: 300px; opacity: .9; }

@media (max-width: 980px) {
  .staf-layout { grid-template-columns: 1fr; }
  .sidebar { position: sticky; top: 0; z-index: 10; }
}
</style>
