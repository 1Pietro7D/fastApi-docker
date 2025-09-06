<!--
// =============================================================================
// FILE: components/ui/BaseInput.vue
// DESCRIZIONE: Questo è un componente UI di base per un campo di input testuale.
// Centralizza lo stile e il comportamento per tutti i campi di input,
// garantendo coerenza nell'applicazione.
// =============================================================================
-->

<script setup>
// --- PROPS ---
// Definiamo le "props" che questo componente può accettare dall'esterno.
defineProps({
  // `modelValue` è il valore del campo di input. Vue usa questo nome
  // di default per la prop collegata a `v-model`.
  modelValue: {
    type: [String, Number], // Può essere testo o un numero.
    default: '',
  },
  // `label` è il testo dell'etichetta da mostrare sopra il campo.
  label: {
    type: String,
    default: '',
  },
  // `type` è il tipo di input HTML (es. 'text', 'password', 'number').
  type: {
    type: String,
    default: 'text',
  },
  // `placeholder` è il testo segnaposto mostrato quando il campo è vuoto.
  placeholder: {
    type: String,
    default: '',
  },
});

// --- EMITS ---
// Definiamo l'evento `update:modelValue` per far funzionare `v-model`.
const emit = defineEmits(['update:modelValue']);

// --- GESTIONE EVENTI ---
// Questa funzione viene chiamata ogni volta che l'utente digita qualcosa
// nel campo di input (grazie a `@input` nel template).
function onInput(event) {
  // Emettiamo l'evento con il nuovo valore del campo.
  // Questo aggiorna la variabile collegata con `v-model` nel componente genitore.
  emit('update:modelValue', event.target.value);
}
</script>

<template>
  <!-- Il template contiene un contenitore, un'etichetta (label) e il campo di input. -->
  <div class="input-wrapper">
    <!-- L'etichetta viene mostrata solo se la prop `label` è stata fornita. -->
    <label v-if="label" class="input-label">{{ label }}</label>
    <!-- Questo è il campo di input HTML. -->
    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      class="input-field"
      @input="onInput"
    />
  </div>
</template>

<style scoped>
/* Stili specifici per questo componente. */
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  width: 100%;
}

.input-label {
  font-family: var(--semantic-font-style-label-md-font-family);
  font-size: var(--semantic-font-style-label-md-font-size);
  font-weight: var(--semantic-font-style-label-md-font-weight);
  color: var(--semantic-color-text-secondary);
}

.input-field {
  font-family: var(--semantic-font-style-body-base-font-family);
  font-size: var(--semantic-font-style-body-base-font-size);
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  /* Transizione fluida per il focus. */
  transition: box-shadow var(--base-animation-duration-fast), border-color var(--base-animation-duration-fast);
}

/* Stile per il testo segnaposto. */
.input-field::placeholder {
  color: var(--semantic-color-text-tertiary);
}

/* Stile quando il campo riceve il focus. */
.input-field:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/* Stile quando il campo è disabilitato. */
.input-field:disabled {
  background-color: var(--semantic-color-surface-disabled);
  color: var(--semantic-color-text-disabled);
  cursor: not-allowed;
}
</style>
