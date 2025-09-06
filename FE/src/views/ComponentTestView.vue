<!--
// =============================================================================
// FILE: views/ComponentTestView.vue
// DESCRIZIONE: Questa è una vista speciale creata per lo sviluppo e il test.
// Il suo scopo è quello di fornire una "sandbox" o "vetrina" dove si possono
// visualizzare e testare i componenti UI di base (`BaseInput`, `BaseSelect`, ecc.)
// in isolamento, per assicurarsi che funzionino correttamente.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { ref } from 'vue'; // Per creare variabili reattive.
// Importiamo i componenti UI che vogliamo testare.
import BaseInput from '../components/ui/BaseInput.vue';
import BaseSelect from '../components/ui/BaseSelect.vue';
import BaseCheckbox from '../components/ui/BaseCheckbox.vue';

// --- LOGICA DEL COMPONENTE ---
// Creiamo delle variabili reattive per "collegarle" ai componenti
// tramite `v-model`. Questo ci permette di vedere i loro valori cambiare in tempo reale.

// Valore per il campo di testo.
const textValue = ref('Some text');
// Valore per il menu a tendina.
const selectValue = ref('b');
// Valore per la checkbox (vero/falso).
const checkboxValue = ref(true);

// Dati di esempio per le opzioni del menu a tendina.
const selectOptions = [
  { value: 'a', text: 'Option A' },
  { value: 'b', text: 'Option B' },
  { value: 'c', text: 'Option C' },
];
</script>

<template>
  <!-- Il template organizza i componenti in sezioni per una facile visualizzazione. -->
  <div class="test-page">
    <h1>Component Test Page</h1>

    <!-- Sezione per BaseInput -->
    <section class="component-group">
      <h2>BaseInput</h2>
      <!-- Usiamo v-model per il "two-way data binding": se l'utente scrive
           nell'input, `textValue` si aggiorna. Se cambiamo `textValue` nel codice,
           il testo nell'input si aggiorna. -->
      <BaseInput v-model="textValue" label="Text Input" />
      <!-- Visualizziamo il valore corrente della variabile per il debug. -->
      <pre>Value: {{ textValue }}</pre>
    </section>

    <!-- Sezione per BaseSelect -->
    <section class="component-group">
      <h2>BaseSelect</h2>
      <BaseSelect v-model="selectValue" label="Select Dropdown" :options="selectOptions" />
      <pre>Value: {{ selectValue }}</pre>
    </section>

    <!-- Sezione per BaseCheckbox -->
    <section class="component-group">
      <h2>BaseCheckbox</h2>
      <BaseCheckbox v-model="checkboxValue" label="Checkbox" />
      <pre>Value: {{ checkboxValue }}</pre>
    </section>
  </div>
</template>

<style scoped>
/* Stili specifici per questa pagina di test, per renderla più leggibile. */
.test-page {
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xl);
  flex-grow: 1;
}
h1, h2 {
  font-family: var(--base-font-family-palette-sans-serif);
}
h1 {
  font-size: var(--base-font-size-2xl);
}
h2 {
  font-size: var(--base-font-size-xl);
}
.component-group {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  padding: var(--semantic-size-inset-lg);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
}
pre {
  font-family: var(--base-font-family-palette-monospace);
  background-color: var(--semantic-color-surface-secondary);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-interactive);
}
</style>
