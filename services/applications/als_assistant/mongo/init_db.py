from src.applications.als_assistant.database.ao.ao_database import get_collection as get_ao_collection
from src.applications.als_assistant.database.logbook.logbook_database import get_collection as get_logbook_collection

get_ao_collection(auto_load=True, hard_reset=True, validate=True)
print("AO DB initialization complete.")
     
get_logbook_collection(auto_load=True, hard_reset=False)
print("Logbook DB initialization complete.")