import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- Google Sheets setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# Open your spreadsheet and Scores worksheet
sheet = client.open("Precon League").worksheet("Scores")

# Load data into DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Streamlit UI setup ---
st.set_page_config(page_title="Grumpy Goblins HQ", layout="wide")
st.title("🎲 Grumpy Goblins HQ - Upgrade Points Tracker")

tab1, tab2 = st.tabs(["📊 Scores Tracker", "📜 Rules"])

# --- Tab 1: Scores Tracker ---
with tab1:
    st.write("### Current Scores")
    st.table(df.set_index('Player'))

    st.header("Add Points")
    player = st.selectbox("Select Player", df['Player'])
    point_type = st.selectbox("Select Point Type", [
        'Upgrade Points Earned',
        'Upgrade Points Available',
        'Upgrade Points Spent'
    ])
    points = st.number_input("Points to Add", min_value=0, step=1)

    if st.button("Add Points"):
        df.loc[df['Player'] == player, point_type] += points
        sheet.resize(rows=1)  # clear except headers
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success(f"Added {points} to {player}'s {point_type}!")
        st.experimental_rerun()

    st.header("Reset Points")
    if st.button("Reset All Points"):
        for col in ['Upgrade Points Earned', 'Upgrade Points Available', 'Upgrade Points Spent']:
            df[col] = 0
        sheet.resize(rows=1)
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.warning("All points reset to zero!")
        st.experimental_rerun()

# --- Tab 2: Rules ---
with tab2:
    st.header("📜 League Rules")
    st.markdown("""
**Gameplay and Scoring**

Games are played in pods as normal multiplayer Commander.

After each game:

- Winner receives 0 upgrade points.
- Each losing player receives 5 upgrade points.

**Bonus Objectives**

- Before each game, 3 random bonus objectives will be drawn.
- Players can earn additional upgrade points by completing these objectives during the game.
- Each objective completed awards 1 point, unless otherwise stated.

**Streak System (Comeback Mechanic)**

- For every consecutive loss, a player earns +1 bonus upgrade point.
- Example: 2 losses in a row = 5 (base) + 2 (streak) = 7 points.
- Streak resets after a win.

**Spending Upgrade Points**

Between game sessions, players may use their upgrade points to build a custom sideboard of cards.
Cards from the sideboard may be swapped into the main deck between games.

Upgrade Costs:

- Basic Lands: 0 points
- Non-Basic & Utility Lands: 1 point each
- Common/Uncommon Cards: 1 point each
- Rare/Mythic Rare Cards: 3 points each
- Game Changer Cards: 7 points each

Only available to players after they’ve hit a 3-game loss streak.

These are high-impact cards that can swing a game.

**League Goals**

- Accessible to all skill levels
- Encouraging gradual deck evolution
- Focused on fun, camaraderie, and clever deckbuilding over time

*Let the games begin, and may your upgrades be epic!*
""")
