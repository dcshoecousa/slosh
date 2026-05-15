<template>
  <article class="stat-card">
    <div class="stat-card__header">
      <span class="stat-card__title">{{ title }}</span>
      <span class="stat-card__chip">{{ chip }}</span>
    </div>
    <strong class="stat-card__value">{{ value }}</strong>
    <p class="stat-card__hint">{{ hint }}</p>
  </article>
</template>

<script>
export default {
  name: "StatCard",
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    hint: {
      type: String,
      default: ""
    },
    chip: {
      type: String,
      default: "Live"
    }
  }
};
</script>
