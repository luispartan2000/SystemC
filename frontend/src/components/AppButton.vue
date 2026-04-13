<template>
  <button :type="type" class="app-btn" :style="customStyle">
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  type: { type: String, default: "button" },
  color: { type: String, default: "#5468ff" }
})
const customStyle = computed(() => ({
  background: props.color
}))
</script>

<style scoped>
.app-btn {
  width: 100%;
  padding: 0.7em;
  color: #fff;
  font-weight: bold;
  font-size: 1.08em;
  border: none;
  border-radius: 6px;
  margin-top: 1em;
  cursor: pointer;
  box-shadow: 0 2px 10px #5468ff25;
  transition: background 0.2s;
}
.app-btn:hover {
  background: #3746a2;
}
</style>
