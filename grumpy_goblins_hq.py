import streamlit as st
import gspread
import pandas as pd
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets auth using Streamlit secrets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open your Google Sheets workbook and worksheets
sh = client.open("Precon League")
scores_ws = sh.worksheet("Scores")

# Load scores data into DataFrame
data = scores_ws.get_all_records()
df = pd.DataFrame(data)

# Sidebar with Tabs
tab = st.sidebar.radio("Navigate", ["Tracker", "Rules"])

if tab == "Tracker":
    st.title("🎲 Grumpy Goblins HQ - Upgrade Points Tracker")

    st.write("### Current Scores")
    st.table(df.set_index("Player"))

    st.header("Add Points")

    player = st.selectbox("Select Player", df["Player"])
    point_type = st.selectbox(
        "Select Point Type",
        ["Upgrade Points Earned", "Upgrade Points Available", "Upgrade Points Spent"],
    )
    points = st.number_input("Points to Add", min_value=0, step=1)

    if st.button("Add Points"):
        # Update local DataFrame
        df.loc[df["Player"] == player, point_type] += points
        # Update Google Sheet
        scores_ws.resize(rows=1)  # clear all except headers
        scores_ws.update([df.columns.values.tolist()] + df.values.tolist())
        st.success(f"Added {points} to {player}'s {point_type}!")
        st.experimental_rerun()

    st.header("Reset Points")
    if st.button("Reset All Points"):
        for col in ["Upgrade Points Earned", "Upgrade Points Available", "Upgrade Points Spent"]:
            df[col] = 0
        scores_ws.resize(rows=1)
        scores_ws.update([df.columns.values.tolist()] + df.values.tolist())
        st.warning("All points reset to zero!")
        st.experimental_rerun()

elif tab == "Rules":
    st.title("📜 League Rules & Gameplay")

    rules_text = """
**Gameplay and Scoring**

- Games are played in pods as normal multiplayer Commander.

- After each game:
  - Winner receives 0 upgrade points.
  - Each losing player receives 5 upgrade points.

**Bonus Objectives**

- Before each game, 3 random bonus objectives will be drawn.
- Players can earn additional upgrade points by completing these objectives during the game.
- Each objective completed awards 1 point, unless otherwise stated.

**Streak System (Comeback Mechanic)**

- For every consecutive loss, a player earns +1 bonus upgrade point.
- Example: 2 losses in a row = 5 (base) + 2 (streak) = 7 points
- Streak resets after a win.

**Spending Upgrade Points**

- Between game sessions, players may use their upgrade points to build a custom sideboard of cards.
- Cards from the sideboard may be swapped into the main deck between games.

**Upgrade Costs:**

- Basic Lands: 0 points
- Non-Basic & Utility Lands: 1 point each
- Common/Uncommon Cards: 1 point each
- Rare/Mythic Rare Cards: 3 points each
- Game Changer Cards: 7 points each
- Only available to players after they’ve hit a 3-game loss streak.
- These are high-impact cards that can swing a game.

**League Goals**

- This league is designed to be:
  - Accessible to all skill levels
  - Encouraging gradual deck evolution
  - Focused on fun, camaraderie, and clever deckbuilding over time

*Let the games begin, and may your upgrades be epic!*
"""
    st.markdown(rules_text)
