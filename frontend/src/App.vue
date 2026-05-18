<template>
  <router-view />
</template>

<script>
import { initializeTheme } from "@/utils/theme";

export default {
  name: "AppRoot",
  created() {
    initializeTheme();
  }
};
</script>
