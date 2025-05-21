import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Tasks from '../views/Tasks.vue'
import Exercises from '../views/Exercises.vue'
import Cycles from '../views/Cycles.vue'
import Timer from '../views/Timer.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks
  },
  {
    path: '/exercises',
    name: 'Exercises',
    component: Exercises
  },
  {
    path: '/cycles',
    name: 'Cycles',
    component: Cycles
  },
  {
    path: '/timer',
    name: 'Timer',
    component: Timer
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router