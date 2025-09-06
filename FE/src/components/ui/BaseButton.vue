<!--
// =============================================================================
// FILE: components/ui/BaseButton.vue
// DESCRIZIONE: Componente di base per un pulsante, ora con supporto per
// varianti "primary" e "secondary" per diverse priorità di azione.
// =============================================================================
-->
<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'primary', // 'primary' o 'secondary'
    validator: (value) => ['primary', 'secondary'].includes(value),
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['medium', 'small'].includes(value),
  }
});

const buttonClass = computed(() => `button button--${props.variant} button--${props.size}`);
</script>

<template>
  <button :class="buttonClass">
    <slot></slot>
  </button>
</template>

<style scoped>
/* Stili di base comuni a tutte le varianti */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--base-size-spacing-2);
  border-radius: var(--semantic-border-radius-interactive);
  border: var(--base-border-width-1) solid transparent; /* Bordo trasparente per mantenere le dimensioni */
  cursor: pointer;
  transition: all var(--base-animation-duration-fast);
}

/* Stili per dimensione Medium (default) */
.button--medium {
  font: var(--semantic-font-style-button-label-medium);
  padding-block: var(--semantic-size-button-padding-block-medium-mobile);
  padding-inline: var(--semantic-size-button-padding-inline-medium-mobile);
}
@media (min-width: 768px) {
  .button--medium {
    padding-block: var(--semantic-size-button-padding-block-medium-tablet);
    padding-inline: var(--semantic-size-button-padding-inline-medium-tablet);
  }
}
@media (min-width: 1024px) {
  .button--medium {
    padding-block: var(--semantic-size-button-padding-block-medium-desktop);
    padding-inline: var(--semantic-size-button-padding-inline-medium-desktop);
  }
}

/* Stili per dimensione Small */
.button--small {
  font: var(--semantic-font-style-button-label-small);
  padding-block: var(--semantic-size-button-padding-block-small-mobile);
  padding-inline: var(--semantic-size-button-padding-inline-small-mobile);
}
@media (min-width: 768px) {
  .button--small {
    padding-block: var(--semantic-size-button-padding-block-small-tablet);
    padding-inline: var(--semantic-size-button-padding-inline-small-tablet);
  }
}
@media (min-width: 1024px) {
  .button--small {
    padding-block: var(--semantic-size-button-padding-block-small-desktop);
    padding-inline: var(--semantic-size-button-padding-inline-small-desktop);
  }
}

.button:focus-visible {
  outline: none;
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/* Variante Primaria */
.button--primary {
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-brand);
}
.button--primary:hover {
  background-color: var(--semantic-color-interactive-primary-hover);
}

/* Variante Secondaria */
.button--secondary {
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-interactive);
  border-color: var(--semantic-color-border-default);
}
.button--secondary:hover {
  background-color: var(--semantic-color-surface-secondary);
  border-color: var(--semantic-color-border-subtle);
}
</style>
