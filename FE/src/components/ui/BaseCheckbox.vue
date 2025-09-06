<!--
// =============================================================================
// FILE: components/ui/BaseCheckbox.vue
// DESCRIZIONE: Questo componente crea una checkbox personalizzata.
// Le checkbox di default dei browser sono difficili da stilizzare in modo
// coerente. Questo componente nasconde la checkbox nativa e la sostituisce
// con una versione personalizzata (`<span>`) che possiamo controllare al 100%.
// =============================================================================
-->

<script setup>
// --- PROPS ---
defineProps({
  // `modelValue` è il valore della checkbox (true o false).
  // Vue usa `modelValue` come nome di default per la prop usata con `v-model`.
  modelValue: {
    type: Boolean,
    default: false,
  },
  // `label` è il testo da visualizzare accanto alla checkbox.
  label: {
    type: String,
    default: '',
  },
});

// --- EMITS ---
// Definiamo l'evento `update:modelValue`, che è necessario per far funzionare `v-model`.
const emit = defineEmits(['update:modelValue']);

// --- GESTIONE EVENTI ---
// Questa funzione viene chiamata quando lo stato della checkbox nativa cambia.
function onChange(event) {
  // Emettiamo l'evento con il nuovo stato (selezionato o meno).
  // Questo aggiornerà la variabile passata tramite `v-model` nel componente genitore.
  emit('update:modelValue', event.target.checked);
}
</script>

<template>
  <!-- Usiamo un tag `<label>` come contenitore principale.
       Questo migliora l'accessibilità: cliccando sul testo (label),
       si attiverà anche la checkbox. -->
  <label class="checkbox-wrapper">
    <!-- Questa è la vera checkbox HTML. La nascondiamo con il CSS,
         ma la manteniamo nel DOM per la sua funzionalità e accessibilità (es. navigazione da tastiera). -->
    <input
      type="checkbox"
      class="checkbox-hidden"
      :checked="modelValue"
      @change="onChange"
    />
    <!-- Questo `<span>` è la nostra checkbox personalizzata, quella che vediamo. -->
    <span class="checkbox-custom"></span>
    <!-- Visualizziamo l'etichetta testuale, se fornita. -->
    <span v-if="label" class="checkbox-label">{{ label }}</span>
  </label>
</template>

<style scoped>
.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  gap: var(--base-size-spacing-2); /* Ridotto lo spazio */
  cursor: pointer;
  /* Altezza di riga ridotta per compattare verticalmente */
  line-height: var(--base-font-line-height-tight);
}

/*
Questa è la tecnica per nascondere un elemento visivamente,
ma mantenerlo accessibile per gli screen reader e la navigazione da tastiera.
*/
.checkbox-hidden {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

/* Stile della nostra checkbox finta. */
.checkbox-custom {
  display: inline-block;
  /* Dimensioni ridotte per la checkbox */
  width: 1.125rem;
  height: 1.125rem;
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--base-border-radius-sm);
  transition: all var(--base-animation-duration-fast);
  flex-shrink: 0; /* Impedisce alla checkbox di restringersi. */
}

.checkbox-label {
  color: var(--semantic-color-text-secondary);
  /* Font ridotto per la label */
  font-size: var(--base-font-size-xs);
}

/* Stile per quando la checkbox è selezionata.
   Il selettore `+` significa "seleziona l'elemento `.checkbox-custom`
   che viene immediatamente dopo un `.checkbox-hidden` che è `:checked`". */
.checkbox-hidden:checked + .checkbox-custom {
  background-color: var(--semantic-color-interactive-primary-default);
  border-color: var(--semantic-color-interactive-primary-default);
  /* Aggiungiamo un'icona di spunta (checkmark) come immagine di sfondo.
     L'SVG è "inlined", cioè scritto direttamente nel CSS. */
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='white'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
}

/* Stile per l'anello di focus per l'accessibilità. */
.checkbox-hidden:focus-visible + .checkbox-custom {
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}
</style>
