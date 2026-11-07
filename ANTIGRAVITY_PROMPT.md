Open this folder in Antigravity and paste:

You are working on AuditMemory, a Streamlit app (app.py) that compares an AI compliance agent with memory OFF vs ON.
RULES: do NOT modify anything inside src/ or data/. Only edit app.py (and add a .streamlit/config.toml for theming).
Keep every function call into src.agent / src.memory / src.eval exactly as is.
GOALS:
1. Make the Live demo tab look like a polished product: clean header with logo text "AuditMemory", dark navy + teal palette.
2. Memory OFF card: muted orange. Memory ON card: green, with a pill "Hindsight memory". Show the memory panel as a timeline of recalled records, coloured by type (finding=red, ticket=amber, policy=blue, slack=grey, feedback=purple), parsing the "[ID] (type, date)" prefix.
3. Make the "Planted issues found" metrics large and animated-looking (use st.metric + progress bars).
4. Keep everything runnable with `streamlit run app.py`; do not add new dependencies.
5. After editing, run the app, take screenshots of the 3 tabs and save them to docs/.
