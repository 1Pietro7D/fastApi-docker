<!--
// =============================================================================
// FILE: components/ui/HamburgerButton.vue
// DESCRIZIONE: Componente UI per un bottone "hamburger" animato.
// Si trasforma in una 'X' quando viene attivato.
// =============================================================================
-->

<script setup>
defineProps({
  // Il componente accetta una prop booleana per determinare lo stato di apertura.
  isOpen: {
    type: Boolean,
    default: false,
  },
});

// Definiamo l'evento che il componente emetterà al click.
defineEmits(['toggle']);
</script>

<template>
  <button
    class="hamburger-button"
    :class="{ 'is-open': isOpen }"
    @click="$emit('toggle')"
    aria-label="Toggle menu"
  >
    <span class="hamburger-box">
      <span class="hamburger-inner"></span>
    </span>
  </button>
</template>

<style scoped>
.hamburger-button {
  display: inline-block;
  cursor: pointer;
  background-color: transparent;
  border: none;
  padding: 10px;
  /* Rimuoviamo l'outline di default del browser quando il bottone è in focus */
  &:focus {
    outline: none;
  }
}

.hamburger-box {
  width: 30px;
  height: 24px;
  display: inline-block;
  position: relative;
}

.hamburger-inner {
  display: block;
  top: 50%;
  margin-top: -2px;
}

.hamburger-inner,
.hamburger-inner::before,
.hamburger-inner::after {
  width: 30px;
  height: 3px;
  background-color: var(--semantic-color-text-primary);
  border-radius: 4px;
  position: absolute;
  transition-property: transform;
  transition-duration: 0.15s;
  transition-timing-function: ease;
}

.hamburger-inner::before,
.hamburger-inner::after {
  content: '';
  display: block;
}

.hamburger-inner::before {
  top: -10px;
}

.hamburger-inner::after {
  bottom: -10px;
}

/* --- Animazione per lo stato "is-open" --- */

/* Nascondiamo la linea centrale */
.hamburger-button.is-open .hamburger-inner {
  transform: rotate(45deg);
}

/* Ruotiamo la linea superiore */
.hamburger-button.is-open .hamburger-inner::before {
  top: 0;
  transform: rotate(-90deg);
}

/* Nascondiamo la linea inferiore (la spostiamo sulla linea centrale) */
.hamburger-button.is-open .hamburger-inner::after {
  bottom: 0;
  opacity: 0;
}

/* Un'animazione più fluida per la X */
.hamburger-button.is-open .hamburger-inner {
    background-color: transparent;
}
.hamburger-button.is-open .hamburger-inner::before {
    transform: rotate(45deg);
    top: 0;
}
.hamburger-button.is-open .hamburger-inner::after {
    transform: rotate(-45deg);
    bottom: 0;
    opacity: 1;
}
</style>
