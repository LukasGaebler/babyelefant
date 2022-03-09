import Vue from "vue";
import VueRouter from "vue-router";
import camera from "../views/User-Camera.vue";
import admin from "../views/Admin-Home.vue";
import user from "../views/User-Home.vue";
import login from "../views/Login.vue";
import showUsers from "../views/Admin-UserAdministration.vue";
import editUser from "../views/Admin-UserPasswordForm.vue";
import dashboard from "../views/User-Dashboard.vue";
import adminEvents from "../views/Admin-EventAdministration.vue"
//import store from '../store/index'

Vue.use(VueRouter);





const routes = [
  {
    path: "/admin",
    name: "admin",
    component: admin,
    meta: {
      admin: true,
      requiresAuth: true
    },
    children: [
      {
        path: "showAllUsers",
        name: "showUsers",
        component: showUsers,
        meta: {
          admin: true,
          requiresAuth: true
        }
      },
      {
        path: "/changePassword/:id",
        name: "editUser",
        component: editUser,
        meta: {
          admin: true,
          requiresAuth: true
        }
      },
      {
        path: "/events",
        name: "adminEvents",
        component: adminEvents,
        meta: {
          admin: true,
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: "/user",
    name: "user",
    component: user,
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: "camera/:eventId",
        name: "camera",
        component: camera,
        meta: {
          requiresAuth: true
        }
      },
      {
        path: "dashboard",
        name: "dashboard",
        component: dashboard,
        meta: {
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: "*",
    name: "login",
    component: login
  }
];

const router = new VueRouter({
  routes
});

router.beforeEach((to, from, next) => {
  if (localStorage.getItem("user") != undefined) {
    if (new Date(JSON.parse(localStorage.getItem("user")).sub.exp).getTime() < Date.now()) {
      next({
        path: '/',
        params: { nextUrl: to.fullPath }
      })
      localStorage.clear();
      next({name: 'login'});
    }
  }

  if (localStorage.getItem('token') != null && !to.matched.some(record => record.meta.requiresAuth) && !localStorage.getItem('token').sub.admin) {
    next({ name: 'dashboard' })
  }

  if (localStorage.getItem('token') != null && !to.matched.some(record => record.meta.requiresAuth) && localStorage.getItem('token').sub.admin) {
    next({ name: 'admin' })
  }

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (localStorage.getItem('token') == null) {
      next({
        path: '/',
        params: { nextUrl: to.fullPath }
      })
    } else {
      let user = JSON.parse(localStorage.getItem('user'))
      if (to.matched.some(record => record.meta.is_admin)) {
        if (user.admin == 1) {
          next()
        }
        else {
          next({ name: 'user' })
        }
      } else {
        next()
      }
    }
  } else {
    next()
  }
})


export default router;
