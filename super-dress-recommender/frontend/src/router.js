import { createRouter, createWebHashHistory } from 'vue-router'
import AuthView from '../script/AuthView.vue'
import ProfileSetup from '../script/ProfileSetup.vue'
import HomeView from '../script/HomeView.vue'
import UploadPhotoView from '../script/UploadPhotoView.vue'
import StyleMatchView from '../script/StyleMatchView.vue'

const routes = [
  { path: '/', redirect: '/auth' },
  { path: '/auth', component: AuthView },
  { path: '/profile', component: ProfileSetup },
  { path: '/home', component: HomeView },
  { path: '/upload', component: UploadPhotoView },
  { path: '/style-match', component: StyleMatchView }
]

export default createRouter({
  history: createWebHashHistory(),
  routes
})