<template>
  <nav class="nav">
    <RouterLink
      v-for="item in items"
      :key="item.label"
      :to="item.to"
      class="link"
      active-class="active"
    >
      {{ item.label }}
    </RouterLink>
  </nav>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.nav {
  display: flex;
  flex-direction: column;
  gap: .5rem;
}


.link {
  display: block;
  padding: .65rem .8rem;
  border: 2px solid #000;
  border-radius: 10px;
  background: #fff;
  text-decoration: none;
  color: inherit;
  font-weight: 500;
  transition: background .2s;
}

.link:hover {
  background: #f9f9f9;
}


.active {
  background: #fff0d9;
}
</style>
