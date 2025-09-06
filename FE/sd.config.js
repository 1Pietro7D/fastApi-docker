// =============================================================================
// FILE: sd.config.js
// DESCRIZIONE: File di configurazione per Style Dictionary.
// Questo file definisce come i nostri file di token JSON vengono trasformati
// in file CSS utilizzabili nell'applicazione.
// =============================================================================

export default {
  // `source` è un array di percorsi che dice a Style Dictionary dove trovare
  // i file di definizione dei token. Includiamo sia i token di base che quelli semantici.
  source: [
    'tokens/base/**/*.json',
    'tokens/semantic/**/*.json'
  ],

  // `platforms` definisce i diversi output che vogliamo generare.
  // In questo caso, generiamo solo CSS.
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      // `files` è un array che ci permette di generare più file di output
      // dalla stessa fonte di token, applicando filtri diversi.
      files: [
        // --- 1. File dei token di base (_base.css) ---
        // Questo file contiene solo i valori primitivi (la nostra palette).
        // È considerato "privato" e non dovrebbe essere usato direttamente nei componenti.
        {
          destination: '_base.css',
          format: 'css/variables',
          options: {
            selector: ':root',
            // `outputReferences: false` assicura che vengano emessi i valori grezzi (es. #ffffff).
            outputReferences: false,
          },
          // Filtriamo per includere solo i token che provengono dalla cartella 'base'.
          filter: (token) => token.filePath.startsWith('tokens/base/')
        },
        // --- 2. File dei token semantici (tokens.css) ---
        // Questo file contiene i token contestuali (es. `colore-testo-primario`).
        // È il file "pubblico" che l'applicazione deve usare.
        {
          destination: 'tokens.css',
          format: 'css/variables',
          options: {
            selector: ':root',
            // `outputReferences: true` è la chiave: emette riferimenti ad altre variabili
            // (es. `var(--base-color-white)`), creando il collegamento tra semantico e base.
            outputReferences: true,
          },
          // Filtriamo per includere solo i token che provengono dalla cartella 'semantic'.
          filter: (token) => token.filePath.startsWith('tokens/semantic/')
        }
      ]
    }
  }
};
