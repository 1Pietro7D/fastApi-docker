<!--
// =============================================================================
// FILE: components/trades/NewTradeForm.vue
// DESCRIZIONE: Questo è un componente specifico che rappresenta il form
// per inserire un nuovo trade. Viene tipicamente usato all'interno di una
// finestra modale.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { ref } from 'vue';
import BaseInput from '../ui/BaseInput.vue';
import BaseButton from '../ui/BaseButton.vue';

// --- EMITS ---
// Definiamo un evento `submit` che verrà emesso quando il form viene inviato.
// Il genitore (es. `DashboardView`) ascolterà questo evento per ricevere i dati.
const emit = defineEmits(['submit']);

// --- STATO LOCALE DEL FORM ---
// Usiamo `ref` per creare un oggetto reattivo che conterrà i valori
// dei campi del form. Questo è lo "stato locale" del componente.
const form = ref({
  ticker: '',
  pnl: 0,
  setup: '',
});

// --- GESTIONE EVENTI ---
// Funzione chiamata quando il form viene inviato.
const handleSubmit = () => {
  // Qui si potrebbe aggiungere della logica di validazione prima di inviare.

  // Emettiamo l'evento `submit`, passando una copia dei dati del form.
  // Usiamo `{ ...form.value }` per creare una copia e non passare
  // direttamente l'oggetto reattivo.
  emit('submit', { ...form.value });

  // Svuotiamo il form dopo l'invio per prepararlo a un nuovo inserimento.
  form.value = { ticker: '', pnl: 0, setup: '' };
};
</script>

<template>
  <!--
  Usiamo un tag `<form>`. `@submit.prevent` è un gestore di eventi di Vue:
  - `@submit`: Ascolta l'evento di invio del form (es. premendo Invio o cliccando un bottone type="submit").
  - `.prevent`: È un "modificatore" che previene il comportamento di default del browser,
    che sarebbe quello di ricaricare la pagina.
  -->
  <form class="new-trade-form" @submit.prevent="handleSubmit">
    <!-- Usiamo i nostri componenti UI di base per costruire il form.
         `v-model` collega ogni campo a una proprietà del nostro oggetto `form`. -->
    <BaseInput v-model="form.ticker" label="Ticker" placeholder="e.g., AAPL" />
    <!-- `.number` è un modificatore di v-model che converte automaticamente l'input in un numero. -->
    <BaseInput v-model.number="form.pnl" label="Net P&L" type="number" step="0.01" />
    <BaseInput v-model="form.setup" label="Setup / Strategy" placeholder="e.g., Breakout" />

    <div class="form-actions">
      <!-- Un bottone di tipo "submit" attiverà l'evento `@submit` del form. -->
      <BaseButton type="submit">Save Trade</BaseButton>
    </div>
  </form>
</template>

<style scoped>
.new-trade-form {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}
.form-actions {
  margin-top: var(--semantic-size-stack-md);
  display: flex;
  justify-content: flex-end; /* Allinea il bottone a destra. */
}
</style>
