<!--
// =============================================================================
// FILE: components/ui/BaseSelect.vue
// DESCRIZIONE: Questo è un componente UI di base per un menu a tendina (select).
// Centralizza lo stile per garantire che tutti i menu a tendina
// nell'applicazione abbiano un aspetto coerente.
// =============================================================================
-->

<script setup>
// --- PROPS ---
defineProps({
  // `modelValue` è il valore attualmente selezionato nel menu.
  // È la prop usata da `v-model`.
  modelValue: {
    type: [String, Number],
    default: '',
  },
  // `label` è l'etichetta da mostrare sopra il menu.
  label: {
    type: String,
    default: '',
  },
  // `options` è un array di oggetti che popola le opzioni del menu.
  // Ogni oggetto deve avere una chiave `value` e una `text`.
  // Esempio: [{ value: '1', text: 'Opzione 1' }]
  options: {
    type: Array,
    required: true,
  },
});

// --- EMITS ---
// Definiamo l'evento per far funzionare `v-model`.
const emit = defineEmits(['update:modelValue']);

// --- GESTIONE EVENTI ---
// Funzione chiamata quando l'utente seleziona una nuova opzione.
function onChange(event) {
  // Emettiamo il nuovo valore selezionato.
  emit('update:modelValue', event.target.value);
}
</script>

<template>
  <div class="select-wrapper">
    <label v-if="label" class="select-label">{{ label }}</label>
    <div class="select-container">
      <!-- Questo è l'elemento <select> nativo del browser. -->
      <select class="select-field" :value="modelValue" @change="onChange">
        <!-- Usiamo `v-for` per creare un tag `<option>` per ogni
             elemento nell'array `options` ricevuto tramite props. -->
        <option v-for="option in options" :key="option.value" :value="option.value">
          {{ option.text }}
        </option>
      </select>
    </div>
  </div>
</template>

<style scoped>
.select-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  width: 100%;
}

.select-label {
  font-family: var(--semantic-font-style-label-md-font-family);
  font-size: var(--semantic-font-style-label-md-font-size);
  font-weight: var(--semantic-font-style-label-md-font-weight);
  color: var(--semantic-color-text-secondary);
}

.select-container {
  position: relative; /* Necessario per posizionare la freccia custom. */
}

.select-field {
  /* Reset dell'aspetto di default del browser per poterlo stilizzare. */
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  cursor: pointer;

  /* Stili condivisi con BaseInput per coerenza. */
  font-family: var(--semantic-font-style-body-base-font-family);
  font-size: var(--semantic-font-style-body-base-font-size);
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-interactive);
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  padding-right: var(--semantic-size-inset-xl); /* Spazio extra a destra per la freccia. */
  transition: box-shadow var(--base-animation-duration-fast), border-color var(--base-animation-duration-fast);
}

/*
Questa è la tecnica per creare una freccia personalizzata, dato che quella
di default non è stilizzabile. Usiamo un pseudo-elemento `::after` sul contenitore.
*/
.select-container::after {
  content: '';
  position: absolute;
  top: 50%;
  right: var(--semantic-size-inset-md);
  transform: translateY(-50%);
  width: 1em; /* Usiamo 'em' per renderla proporzionale alla dimensione del font. */
  height: 1em;
  background-color: var(--semantic-color-text-tertiary);
  /* `clip-path` disegna una forma (in questo caso, un triangolo). */
  clip-path: polygon(100% 25%, 50% 75%, 0 25%);
  pointer-events: none; /* Impedisce alla freccia di intercettare i click. */
  transition: background-color var(--base-animation-duration-fast);
}

/* Cambiamo colore alla freccia quando si passa il mouse sopra il select. */
.select-field:hover + .select-container::after {
    background-color: var(--semantic-color-text-primary);
}

/* Stile per il focus. */
.select-field:focus {
  outline: none;
  border-color: var(--semantic-color-border-focus);
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}
</style>
