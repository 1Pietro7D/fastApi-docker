# app/Schemas/role.py

from pydantic import BaseModel
from uuid import UUID

# ✅ Schema per la creazione di un nuovo ruolo (input)
# Usato negli endpoint POST /roles per definire i dati di un nuovo ruolo.
class RoleCreate(BaseModel):
    name: str                       # nome del ruolo (es. "admin", "editor", "user")
    description: str | None = None   # descrizione opzionale del ruolo

# ✅ Schema per l’aggiornamento di un ruolo (input parziale)
# Usato negli endpoint PUT /roles/{id}, entrambi i campi sono opzionali.
class RoleUpdate(BaseModel):
    name: str | None = None          # possibilità di aggiornare il nome del ruolo
    description: str | None = None   # possibilità di aggiornare la descrizione

# ✅ Schema per la lettura di un ruolo (output)
# Definisce i campi restituiti nelle API in risposta, per esempio in GET /roles.
class RoleRead(BaseModel):
    id: UUID                         # PK come UUID (coerente con il DB)
    name: str                        # nome del ruolo
    description: str | None = None   # descrizione del ruolo, se esiste

    class Config:
        # Permette a Pydantic di costruire il modello direttamente da un oggetto ORM (es. SQLAlchemy).
        from_attributes = True
