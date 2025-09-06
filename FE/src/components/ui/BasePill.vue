<template>
  <span class="pill">
    <slot></slot>
  </span>
</template>

<style scoped>
.pill {
  display: inline-block;
  padding: var(--base-size-spacing-1) var(--base-size-spacing-3);
  border-radius: var(--base-border-radius-full);
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-label-sm);
  font-weight: 500;
  text-transform: capitalize;
}
</style>
