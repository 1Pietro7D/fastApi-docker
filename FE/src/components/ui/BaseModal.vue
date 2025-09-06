<!--
// =============================================================================
// FILE: components/ui/BaseModal.vue
// DESCRIZIONE: Questo componente crea una finestra modale (o "popup").
// È un elemento fondamentale per mostrare form, messaggi di conferma o
// dettagli importanti senza dover cambiare pagina.
// =============================================================================
-->

<script setup>
import { watch } from 'vue';

// --- PROPS ---
const props = defineProps({
  // `show` è un booleano che controlla se la modale è visibile o meno.
  // Viene passato dal componente genitore.
  show: {
    type: Boolean,
    default: false,
  },
  // Aggiungiamo una prop per controllare la visibilità del bottone di chiusura
  showCloseButton: {
    type: Boolean,
    default: true,
  },
});

// --- EMITS ---
// Definiamo un evento `close` per permettere al componente genitore
// di sapere quando l'utente vuole chiudere la modale (es. cliccando
// sullo sfondo o sul pulsante di chiusura).
const emit = defineEmits(['close']);

// --- LOGICA ---
// Osserviamo la prop `show` per applicare/rimuovere una classe al body.
// Questo è il meccanismo di "scroll-trapping": quando il modale è aperto,
// il body ha `overflow: hidden` per impedire lo scroll della pagina sottostante.
watch(() => props.show, (isShown) => {
  if (isShown) {
    document.body.classList.add('modal-open');
  } else {
    document.body.classList.remove('modal-open');
  }
});
</script>

<!--
Aggiungiamo un secondo blocco <script> per definire opzioni a livello di componente
che non sono disponibili all'interno di `<script setup>`.
`inheritAttrs: false` dice a Vue di NON applicare automaticamente gli attributi
passati al componente (come `class` o `id`) all'elemento radice.
Lo faremo manualmente con `v-bind="$attrs"` per avere un controllo preciso.
-->
<script>
export default {
  inheritAttrs: false,
};
</script>

<template>
  <!--
  `<Teleport to="body">` è una funzionalità avanzata di Vue.
  Dice a Vue di "teletrasportare" il contenuto di questo template
  e di renderizzarlo direttamente come figlio del tag `<body>` nel DOM.
  Questo è fondamentale per le modali, per evitare problemi di stacking
  (z-index) e di layout causati dai componenti genitori.
  -->
  <Teleport to="body">
    <!--
    `<Transition>` è un altro componente speciale di Vue che permette di
    applicare animazioni di entrata e uscita a un elemento.
    Il `name="modal-fade"` si collega alle classi CSS sottostanti
    (`.modal-fade-enter-active`, ecc.) per creare un effetto di dissolvenza.
    -->
    <Transition name="modal-fade">
      <!--
      Il contenitore principale della modale viene mostrato solo se `show` è true.
      - `@click.self`: Questo modificatore fa sì che l'evento `click` si attivi
        solo se si clicca direttamente su questo `div` (l'overlay scuro) e non
        sui suoi figli (la card bianca). In questo modo, chiudiamo la modale
        cliccando sullo sfondo.
      - `v-bind="$attrs"`: Applichiamo manualmente tutti gli attributi non-prop
        (come `class`) a questo elemento.
      -->
      <div v-if="show" class="modal-overlay" @click.self="emit('close')" v-bind="$attrs">
        <!-- La card (il "foglio" bianco) che contiene il contenuto della modale. -->
        <div class="modal-card">
          <header class="modal-header">
            <!--
            `<slot>` con un nome permette di creare dei "segnaposto nominati".
            Il genitore può fornire contenuto specifico per l'header in questo modo:
            <BaseModal><template #header>Mio Titolo</template></BaseModal>
            Se non viene fornito nulla, mostra il contenuto di default ("Titolo del Modal").
            -->
            <slot name="header">Titolo del Modal</slot>
            <button v-if="showCloseButton" class="close-button" @click="emit('close')">&times;</button>
          </header>

          <main class="modal-body">
            <!-- Questo è lo slot di default, per il contenuto principale. -->
            <slot>Contenuto del Modal</slot>
          </main>

          <footer class="modal-footer">
            <!-- Slot per il footer, tipicamente per i bottoni di azione. -->
            <slot name="footer"></slot>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed; /* Si posiziona rispetto alla finestra del browser. */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, var(--semantic-opacity-50));
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--semantic-layer-z-index-overlay); /* Si assicura che sia sopra tutto. */
}

.modal-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-high);
  padding: var(--semantic-size-component-modal-padding-mobile);
  z-index: var(--semantic-layer-z-index-modal);
  width: 100%;
  max-width: var(--semantic-size-component-modal-max-width-mobile);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-component-modal-gap-mobile);
  max-height: 85vh;
}

@media (min-width: 768px) {
  .modal-card {
    max-width: var(--semantic-size-component-modal-max-width-tablet);
    padding: var(--semantic-size-component-modal-padding-tablet);
    gap: var(--semantic-size-component-modal-gap-tablet);
  }
}

@media (min-width: 1024px) {
  .modal-card {
    max-width: var(--semantic-size-component-modal-max-width-desktop);
    padding: var(--semantic-size-component-modal-padding-desktop);
    gap: var(--semantic-size-component-modal-gap-desktop);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.modal-body {
  flex-grow: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-footer {
    flex-shrink: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: var(--base-font-size-2xl);
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
}

/* Stili per la transizione di dissolvenza. */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity var(--base-animation-duration-base) var(--base-animation-easing-out);
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
