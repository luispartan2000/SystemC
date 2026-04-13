import { createRouter, createWebHistory } from 'vue-router'

// Vistas comunes
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import ChangePasswordView from '../views/ChangePasswordView.vue'
import RecoveryPasswordView from '../views/RecoveryPasswordView.vue'

// Alumno
import AlumnoLayout from '../views/alum/AlumnoLayout.vue'
import AlumnoHome from '../views/alum/AlumnoHome.vue'
import AlumnoCursos from '../views/alum/AlumnoCursos.vue'

// Staf
import StafLayout from '../views/staf/StafLayout.vue'
import StafHome from '../views/staf/StafHome.vue'
import ValidarAlumnos from '../views/staf/ValidarAlumnos.vue'
import StafVouchers from '../views/staf/StafVouchers.vue'
import StafInscripciones from '../views/staf/StafInscripciones.vue'

// Admin
import AdminLayout from '../views/admin/AdminLayout.vue'
import AdminHome from '../views/admin/AdminHome.vue'
import AdminGestionarStafs from '../views/admin/AdminGestionarStafs.vue'
import AdminCursos from '../views/admin/AdminCursos.vue'
// (si decides usarlo más adelante)
// import AdminInscripciones from '../views/admin/AdminInscripciones.vue'

const routes = [
  { path: '/registro', component: RegisterView },
  { path: '/cambiar-contrasena', component: ChangePasswordView },
  { path: '/recuperar-password', component: RecoveryPasswordView },
  { path: '/', component: LoginView },

  // ------------------------------
  // Alumno
  // ------------------------------
  {
    path: '/home-alum',
    component: AlumnoLayout,
    meta: { requiereAuth: true, tipo: 'ALUMNO' },
    children: [
      { path: '', name: 'alum-home', component: AlumnoHome },
      { path: 'cursos', name: 'alum-cursos', component: AlumnoCursos },
    ],
  },

  // ------------------------------
  // Staf
  // ------------------------------
  {
    path: '/staf',
    component: StafLayout,
    meta: { requiereAuth: true, tipo: 'STAF' },
    children: [
      { path: '', name: 'staf-home', component: StafHome },
      {
        path: 'validar',
        name: 'staf-validar',
        component: ValidarAlumnos,
        meta: { requiereAuth: true, tipo: 'STAF' },
      },
      {
        path: 'vouchers',
        name: 'staf-vouchers',
        component: StafVouchers,
        meta: { requiereAuth: true, tipo: 'STAF' },
      },
      {
        path: 'inscripciones',
        name: 'staf-inscripciones',
        component: StafInscripciones,
        meta: { requiereAuth: true, tipo: 'STAF' },
      },
    ],
  },

  // ------------------------------
  // Admin
  // ------------------------------
  {
    path: '/admin-panel',
    component: AdminLayout,
    meta: { requiereAuth: true, tipo: 'ADMIN' },
    children: [
      { path: '', name: 'admin-home', component: AdminHome },
      {
        path: 'gestionarstafs',
        name: 'admin-gestionarstafs',
        component: AdminGestionarStafs,
      },
      {
        path: 'cursos',
        name: 'admin-cursos',
        component: AdminCursos,
      },
      // si quieres usarlo más adelante
      // {
      //   path: 'inscripciones',
      //   name: 'admin-inscripciones',
      //   component: AdminInscripciones,
      // },
    ],
  },

  { path: '/admin-login', component: AdminLoginView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function homeByRole(tipo) {
  if (tipo === 'ALUMNO') return '/home-alum'
  if (tipo === 'STAF') return '/staf'
  if (tipo === 'ADMIN') return '/admin-panel'
  return '/'
}

router.beforeEach(async (to, from, next) => {
  if (to.path === '/recuperar-password' || to.path === '/cambiar-contrasena') {
    return next()
  }

  if (to.meta.requiereAuth) {
    try {
      const res = await fetch('http://localhost:8000/api/whoami/', {
        credentials: 'include',
      })

      if (res.ok) {
        const user = await res.json()

        if (user.must_change_password) {
          if (to.path !== '/cambiar-contrasena') {
            return next({ path: '/cambiar-contrasena' })
          }
        } else {
          if (to.path === '/cambiar-contrasena') {
            return next({ path: homeByRole(user.tipo), replace: true })
          }
        }

        if (to.meta.tipo && user.tipo !== to.meta.tipo) {
          return next({ path: homeByRole(user.tipo) })
        }
        return next()
      } else {
        return next({ path: '/' })
      }
    } catch (err) {
      return next({ path: '/' })
    }
  } else {
    try {
      const res = await fetch('http://localhost:8000/api/whoami/', {
        credentials: 'include',
      })
      if (res.ok) {
        const user = await res.json()
        if (to.path === '/' || to.path === '/admin-login') {
          return next({ path: homeByRole(user.tipo), replace: true })
        }
      }
    } catch (e) {}
    return next()
  }
})

export default router
