<script setup>
import { ref } from 'vue'
import AuthView from './AuthView.vue'
import ProfileSetup from './ProfileSetup.vue'
import HomeView from './HomeView.vue'
import UploadPhotoView from './UploadPhotoView.vue'
import StyleMatchView from './StyleMatchView.vue'

const currentPage = ref('auth')

const handleLoginSuccess = () => {
  currentPage.value = 'profile'
}

const handleProfileComplete = () => {
  currentPage.value = 'home'
}

const handleUploadPhotoClicked = () => {
  currentPage.value = 'upload'
}

const handleBackToHome = () => {
  currentPage.value = 'home'
}

const handleGoToProfile = () => {
  currentPage.value = 'profile'
}

const handleGoToStyleMatch = () => {
  currentPage.value = 'style-match'
}

const handleBackFromStyleMatch = () => {
  currentPage.value = 'home'
}
</script>

<template>
  <div id="app-container">
    <Transition name="page-fade" mode="out-in">
      <AuthView
        v-if="currentPage === 'auth'"
        key="auth"
        @login-success="handleLoginSuccess"
      />

      <ProfileSetup
        v-else-if="currentPage === 'profile'"
        key="profile"
        @profile-complete="handleProfileComplete"
      />

      <HomeView
        v-else-if="currentPage === 'home'"
        key="home"
        @go-to-style-match="handleGoToStyleMatch"
        @go-to-profile="handleGoToProfile"
      />

      <UploadPhotoView
        v-else-if="currentPage === 'upload'"
        key="upload"
        @back-to-home="handleBackToHome"
      />

      <StyleMatchView
        v-else-if="currentPage === 'style-match'"
        key="style-match"
        @back-to-home="handleBackFromStyleMatch"
      />

    </Transition>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

html, body, #app {
  margin: 0;
  padding: 0;
  min-height: 100%;
}

body {
  font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  background: #f5f5f3;
  color: #1f1f1f;
}

#app-container {
  min-height: 100vh;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
  transform-origin: center center;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
  transform: scale(0.992);
}

</style>