<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLoginSuccess = () => router.push('/profile')
const handleProfileComplete = () => router.push('/home')
const handleGoToProfile = () => router.push('/profile')
const handleGoToStyleMatch = () => router.push('/style-match')
const handleBackToHome = () => router.push('/home')
</script>

<template>
  <div id="app-container">
    <RouterView v-slot="{ Component, route }">
      <Transition name="page-fade" mode="out-in">
        <component
          :is="Component"
          :key="route.fullPath"
          @login-success="handleLoginSuccess"
          @profile-complete="handleProfileComplete"
          @go-to-style-match="handleGoToStyleMatch"
          @go-to-profile="handleGoToProfile"
          @back-to-home="handleBackToHome"
        />
      </Transition>
    </RouterView>
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