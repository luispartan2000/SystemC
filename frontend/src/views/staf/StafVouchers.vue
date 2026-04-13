<template>
  <div>
    <h1>Revisión de Pagos (Vouchers)</h1>

    <div class="card">
      <div v-if="loading" class="loading">Cargando inscripciones…</div>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Alumno</th>
            <th>Curso</th>
            <th>Estado de Pago</th>
            <th>Voucher</th>
            <th>Monto Faltante</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in inscripciones" :key="i.id">
            <td>
              <strong>{{ i.alumno.nombre }}</strong><br />
              <small>{{ i.alumno.matricula }}</small><br />
              <small>{{ i.alumno.email }}</small>
            </td>
            <td>{{ i.curso.nombre }} (Nivel {{ i.curso.nivel }})</td>
            <td>
              <span :class="'estado ' + i.estado_pago">{{ i.estado_pago }}</span>
            </td>
            <td>
              <a v-if="i.voucher_url" :href="i.voucher_url" target="_blank">Ver voucher</a>
              <span v-else class="muted">No subido</span>
            </td>
            <td>
              <span v-if="i.monto_faltante && i.monto_faltante > 0">
                ${{ i.monto_faltante }}
              </span>
              <span v-else class="muted">—</span>
            </td>
            <td>
              <button class="success" @click="marcarPago(i.id)">Confirmar Pago</button>
              <button class="warning" @click="marcarFaltante(i.id)">Marcar Faltante</button>
            </td>
          </tr>
          <tr v-if="!inscripciones.length">
            <td colspan="6" class="muted">No hay inscripciones</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="msg" :class="msgType" class="msg">{{ msg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const inscripciones = ref([])
const loading = ref(false)
const msg = ref("")
const msgType = ref("")

const getCookie = (n) =>
  (`; ${document.cookie}`).split(`; ${n}=`).pop()?.split(";")[0] || ""

const cargarInscripciones = async () => {
  loading.value = true
  try {
    const res = await fetch("http://localhost:8000/api/staf/inscripciones/", {
      credentials: "include",
    })
    const data = await res.json()
    if (res.ok) {
      inscripciones.value = data.inscripciones || []
    } else {
      inscripciones.value = []
      msg.value = data.error || "Error al cargar inscripciones"
      msgType.value = "error"
    }
  } catch (e) {
    msg.value = "Error de conexión"
    msgType.value = "error"
  } finally {
    loading.value = false
  }
}

const marcarPago = async (id) => {
  try {
    const res = await fetch(
      `http://localhost:8000/api/staf/validar-pago/${id}/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        credentials: "include",
        body: JSON.stringify({ estado_pago: "PAGADO" }),
      }
    )
    const data = await res.json()
    if (res.ok) {
      msg.value = data.success
      msgType.value = "success"
      await cargarInscripciones()
    } else {
      msg.value = data.error || "Error al actualizar"
      msgType.value = "error"
    }
  } catch (e) {
    msg.value = "Error de conexión"
    msgType.value = "error"
  }
}

const marcarFaltante = async (id) => {
  const monto = prompt("¿Cuánto falta por pagar?")
  if (!monto || isNaN(monto)) return

  try {
    const res = await fetch(
      `http://localhost:8000/api/staf/validar-pago/${id}/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        credentials: "include",
        body: JSON.stringify({ estado_pago: "FALTANTE", monto_faltante: monto }),
      }
    )
    const data = await res.json()
    if (res.ok) {
      msg.value = data.success
      msgType.value = "success"
      await cargarInscripciones()
    } else {
      msg.value = data.error || "Error al actualizar"
      msgType.value = "error"
    }
  } catch (e) {
    msg.value = "Error de conexión"
    msgType.value = "error"
  }
}

onMounted(cargarInscripciones)
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
  vertical-align: top;
}
.muted {
  color: #99a;
}
button.success {
  background: #27ae60;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  cursor: pointer;
  margin-right: 0.4rem;
}
button.warning {
  background: #e67e22;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  cursor: pointer;
}
.estado {
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}
.estado.EN_PROCESO {
  background: #f1c40f33;
  color: #c39a00;
}
.estado.EN_REVISION {
  background: #3498db33;
  color: #21618c;
}
.estado.PAGADO {
  background: #27ae6033;
  color: #1e8449;
}
.estado.FALTANTE {
  background: #e74c3c33;
  color: #922b21;
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
