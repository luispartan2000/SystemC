<template>
  <div>
    <h1>Mis Cursos</h1>

    <div class="card">
      <div v-if="loading" class="loading">Cargando cursos…</div>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Curso</th>
            <th>Profesor</th>
            <th>Nivel</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in cursos" :key="c.id">
            <td>{{ c.nombre }}</td>
            <td>{{ c.profesor }}</td>
            <td>{{ c.nivel }}</td>
            <td>
              <span :class="'estado ' + c.estado">{{ c.estado }}</span>
            </td>
            <td>
              <button
                v-if="c.estado === 'DISPONIBLE'"
                class="primary"
                @click="inscribirse(c.id)"
              >
                Inscribirme
              </button>

              <div v-else-if="c.estado === 'EN_PROCESO' || c.estado === 'EN_REVISION'">
                <input
                  type="file"
                  accept="image/*"
                  @change="onFileChange($event, c.id)"
                />
                <button class="upload" @click="subirVoucher(c.id)" :disabled="!files[c.id]">
                  Subir Voucher
                </button>
              </div>

              <span v-else-if="c.estado === 'PAGADO'" class="success">Pago confirmado</span>
              <span v-else-if="c.estado === 'FALTANTE'" class="warning">Pago incompleto</span>
            </td>
          </tr>
          <tr v-if="!cursos.length">
            <td colspan="5" class="muted">No tienes cursos disponibles</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="msg" :class="msgType" class="msg">{{ msg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const cursos = ref([])
const loading = ref(false)
const msg = ref("")
const msgType = ref("")
const files = ref({})

const getCookie = (n) =>
  (`; ${document.cookie}`).split(`; ${n}=`).pop()?.split(";")[0] || ""

const cargarCursos = async () => {
  loading.value = true
  try {
    const res = await fetch("http://localhost:8000/api/alumno/cursos/", {
      credentials: "include",
    })
    const data = await res.json()
    if (res.ok) {
      cursos.value = data.cursos || []
    } else {
      cursos.value = []
      msg.value = data.error || "Error al cargar cursos"
      msgType.value = "error"
    }
  } catch (e) {
    msg.value = "Error de conexión"
    msgType.value = "error"
  } finally {
    loading.value = false
  }
}

const inscribirse = async (id) => {
  try {
    const res = await fetch("http://localhost:8000/api/alumno/inscribirse/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      credentials: "include",
      body: JSON.stringify({ curso_id: id }),
    })
    const data = await res.json()
    if (res.ok) {
      msg.value = data.success
      msgType.value = "success"
      await cargarCursos()
    } else {
      msg.value = data.error || "Error al inscribirse"
      msgType.value = "error"
    }
  } catch (e) {
    msg.value = "Error de conexión"
    msgType.value = "error"
  }
}

const onFileChange = (event, cursoId) => {
  files.value[cursoId] = event.target.files[0]
}

const subirVoucher = async (cursoId) => {
  const file = files.value[cursoId]
  if (!file) return

  const inscripcion = cursos.value.find((c) => c.id === cursoId)
  if (!inscripcion) return

  const formData = new FormData()
  formData.append("voucher", file)

  try {
    const res = await fetch(
      `http://localhost:8000/api/alumno/voucher/${inscripcion.inscripcion_id}/`,
      {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        credentials: "include",
        body: formData,
      }
    )
    const data = await res.json()
    if (res.ok) {
      msg.value = data.success
      msgType.value = "success"
      await cargarCursos()
    } else {
      msg.value = data.error || "Error al subir voucher"
      msgType.value = "error"
    }
  } catch (e) {
    msg.value = "Error de conexión"
    msgType.value = "error"
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
.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.table th,
.table td {
  padding: 0.6rem 0.5rem;
  border-bottom: 1px solid #eee;
  text-align: left;
  vertical-align: middle;
}
.muted {
  color: #99a;
  text-align: center;
}
button.primary {
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  cursor: pointer;
}
button.upload {
  background: #8e44ad;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  margin-top: 0.3rem;
  cursor: pointer;
}
.success {
  color: #27ae60;
  font-weight: bold;
}
.warning {
  color: #e67e22;
  font-weight: bold;
}
.estado {
  font-weight: bold;
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
