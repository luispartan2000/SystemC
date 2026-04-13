<template>
  <div>
    <h1>Gestión de Cursos</h1>

    <form @submit.prevent="guardarCurso" class="card form">
      <div class="grid">
        <input v-model="curso.nombre" placeholder="Nombre del curso" required />
        <input v-model="curso.profesor" placeholder="Profesor" required />
        <input v-model.number="curso.nivel" type="number" min="1" placeholder="Nivel" required />
        <input v-model.number="curso.cupo_minimo" type="number" min="1" placeholder="Cupo mínimo" required />
        <input v-model.number="curso.cupo_maximo" type="number" min="1" placeholder="Cupo máximo" required />
        <input v-model="curso.fecha_limite" type="date" placeholder="Fecha límite" required />

        <div class="field inline">
          <input id="activo" type="checkbox" v-model="curso.activo" />
          <label for="activo">Activo</label>
        </div>
      </div>

      <button type="submit" class="primary">
        {{ curso.id ? "Actualizar Curso" : "Crear Curso" }}
      </button>
      <button v-if="curso.id" type="button" class="secondary" @click="resetForm">
        Cancelar
      </button>

      <div v-if="msg" :class="msgType" class="msg">{{ msg }}</div>
    </form>

    <div class="card">
      <h2>Cursos registrados</h2>
      <div v-if="loading" class="loading">Cargando…</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Nivel</th>
            <th>Profesor</th>
            <th>Cupo</th>
            <th>Fecha límite</th>
            <th>Activo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in cursos" :key="c.id">
            <td>{{ c.nombre }}</td>
            <td>{{ c.nivel }}</td>
            <td>{{ c.profesor }}</td>
            <td>{{ c.cupo_minimo }} - {{ c.cupo_maximo }}</td>
            <td>{{ c.fecha_limite }}</td>
            <td>{{ c.activo ? "Sí" : "No" }}</td>
            <td>
              <button class="edit" @click="editar(c)">Editar</button>
              <button class="danger" @click="eliminar(c.id)">Eliminar</button>
            </td>
          </tr>
          <tr v-if="!cursos.length">
            <td colspan="7" class="muted">Sin registros</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const cursos = ref([])
const loading = ref(false)
const msg = ref("")
const msgType = ref("")

const curso = ref({
  id: null,
  nombre: "",
  nivel: 1,
  profesor: "",
  cupo_minimo: 1,
  cupo_maximo: 30,
  fecha_limite: "",
  activo: true,
})

const getCookie = (n) =>
  (`; ${document.cookie}`).split(`; ${n}=`).pop()?.split(";")[0] || ""

const cargarCursos = async () => {
  loading.value = true
  try {
    const res = await fetch("http://localhost:8000/api/admin/cursos/", {
      credentials: "include",
    })
    const data = await res.json()
    if (res.ok) {
      cursos.value = data.cursos || []
    } else {
      cursos.value = []
    }
  } catch (e) {
    cursos.value = []
  } finally {
    loading.value = false
  }
}

const guardarCurso = async () => {
  msg.value = ""
  try {
    const method = curso.value.id ? "PUT" : "POST"
    const url = curso.value.id
      ? `http://localhost:8000/api/admin/cursos/${curso.value.id}/`
      : "http://localhost:8000/api/admin/cursos/"

    const res = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      credentials: "include",
      body: JSON.stringify(curso.value),
    })

    const data = await res.json()
    if (res.ok) {
      msgType.value = "success"
      msg.value = data.success
      resetForm()
      await cargarCursos()
    } else {
      msgType.value = "error"
      msg.value = data.error || "Error al guardar curso"
    }
  } catch (e) {
    msgType.value = "error"
    msg.value = "Error de conexión"
  }
}

const editar = (c) => {
  curso.value = { ...c }
}

const eliminar = async (id) => {
  if (!confirm("¿Eliminar este curso?")) return
  try {
    const res = await fetch(
      `http://localhost:8000/api/admin/cursos/${id}/`,
      {
        method: "DELETE",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        credentials: "include",
      }
    )
    const data = await res.json()
    if (res.ok) {
      msgType.value = "success"
      msg.value = data.success
      await cargarCursos()
    } else {
      msgType.value = "error"
      msg.value = data.error || "Error al eliminar"
    }
  } catch (e) {
    msgType.value = "error"
    msg.value = "Error de conexión"
  }
}

const resetForm = () => {
  curso.value = {
    id: null,
    nombre: "",
    nivel: 1,
    profesor: "",
    cupo_minimo: 1,
    cupo_maximo: 30,
    fecha_limite: "",
    activo: true,
  }
}

onMounted(cargarCursos)
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  padding: 1.4rem;
  margin-top: 1rem;
}
.form .grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: 0.9rem;
}
input,
select {
  margin: 0;
  padding: 0.9rem 1rem;
  border: none;
  border-radius: 8px;
  background: #f7f8fa;
  color: #26344a;
  font-size: 1rem;
  box-shadow: 0 2px 10px #0001;
  outline: none;
  transition: box-shadow 0.18s;
  width: 100%;
}
input:focus,
select:focus {
  box-shadow: 0 2px 18px #007cf730;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field.inline {
  flex-direction: row;
  align-items: center;
  gap: 0.6rem;
}
.field label {
  font-weight: 700;
  font-size: 0.94rem;
  color: #003b5c;
}
button.primary {
  margin-top: 1rem;
  padding: 0.95rem 1.1rem;
  border: none;
  border-radius: 8px;
  background: #26344a;
  color: #fff;
  font-weight: 800;
  letter-spacing: 1.2px;
  font-size: 1.05rem;
  cursor: pointer;
  box-shadow: 0 2px 14px #203d5a30;
  transition: background 0.16s, transform 0.09s;
}
button.primary:hover {
  background: #495ba1;
  transform: scale(1.03);
}
button.primary:active {
  transform: scale(0.98);
}
button.secondary {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  border: none;
  border-radius: 8px;
  background: #aaa;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  margin-left: 0.5rem;
}
button.edit {
  background: #2980b9;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  cursor: pointer;
  margin-right: 0.3rem;
}
button.danger {
  background: #c0392b;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  cursor: pointer;
}
.loading {
  padding: 0.5rem 0;
  color: #666;
}
.muted {
  color: #99a;
  text-align: center;
}
.msg {
  margin-top: 1rem;
  padding: 0.7rem;
  border-radius: 6px;
}
.success {
  background: #2ecc71;
  color: #fff;
}
.error {
  background: #e74c3c;
  color: #fff;
}
</style>
