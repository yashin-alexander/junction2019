<template>
  <div id="app">
    <video style="height: 0px; opacity: 0;" autoplay></video>
    <YouTube></YouTube>
  </div>
</template>

<script>
import YouTube from './components/YouTube.vue'

export default {
  name: 'app',
  components: {
      YouTube
  }
}
</script>

<style lang="scss">
html, body {
background: black;
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
