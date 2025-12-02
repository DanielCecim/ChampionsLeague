# For Barcelona vs Real Madrid
BARCA_REAL_MERCH = [
  {"stock": {"Barca scarves": 25, "Barca jerseys": 20}, "prices": {"Barca scarves": 15, "Barca jerseys": 80}},
  {"stock": {"Barca hats": 30, "Barca flags": 15}, "prices": {"Barca hats": 10, "Barca flags": 12}},
  {"stock": {"Barca mugs": 20, "Barca keychains": 50}, "prices": {"Barca mugs": 8, "Barca keychains": 5}},
  {"stock": {"Real scarves": 25, "Real jerseys": 20}, "prices": {"Real scarves": 15, "Real jerseys": 85}},
  {"stock": {"Real hats": 30, "Real flags": 15}, "prices": {"Real hats": 12, "Real flags": 10}},
  {"stock": {"Real mugs": 20, "Real keychains": 50}, "prices": {"Real mugs": 8, "Real keychains": 5}},
]

# For Atletico Madrid vs PSG
ATLETICO_PSG_MERCH = [
  {"stock": {"Atletico scarves": 25, "Atletico jerseys": 20}, "prices": {"Atletico scarves": 15, "Atletico jerseys": 80}},
  {"stock": {"Atletico hats": 30, "Atletico flags": 15}, "prices": {"Atletico hats": 10, "Atletico flags": 12}},
  {"stock": {"Atletico mugs": 20, "Atletico keychains": 50}, "prices": {"Atletico mugs": 8, "Atletico keychains": 5}},
  {"stock": {"PSG scarves": 25, "PSG jerseys": 20}, "prices": {"PSG scarves": 15, "PSG jerseys": 85}},
  {"stock": {"PSG hats": 30, "PSG flags": 15}, "prices": {"PSG hats": 12, "PSG flags": 10}},
  {"stock": {"PSG mugs": 20, "PSG keychains": 50}, "prices": {"PSG mugs": 8, "PSG keychains": 5}},
]

# For Finals
FINALS_MERCH_TEMPLATE = {
  "Barcelona": [
    {"stock": {"Barca scarves": 30, "Barca jerseys": 25}, "prices": {"Barca scarves": 15, "Barca jerseys": 80}},
    {"stock": {"Barca hats": 35, "Barca flags": 20}, "prices": {"Barca hats": 10, "Barca flags": 12}},
    {"stock": {"Barca mugs": 25, "Barca keychains": 60}, "prices": {"Barca mugs": 8, "Barca keychains": 5}},
  ],
  "Real Madrid": [
    {"stock": {"Real scarves": 30, "Real jerseys": 25}, "prices": {"Real scarves": 15, "Real jerseys": 85}},
    {"stock": {"Real hats": 35, "Real flags": 20}, "prices": {"Real hats": 12, "Real flags": 10}},
    {"stock": {"Real mugs": 25, "Real keychains": 60}, "prices": {"Real mugs": 8, "Real keychains": 5}},
  ],
  "Atletico Madrid": [
    {"stock": {"Atletico scarves": 30, "Atletico jerseys": 25}, "prices": {"Atletico scarves": 15, "Atletico jerseys": 80}},
    {"stock": {"Atletico hats": 35, "Atletico flags": 20}, "prices": {"Atletico hats": 10, "Atletico flags": 12}},
    {"stock": {"Atletico mugs": 25, "Atletico keychains": 60}, "prices": {"Atletico mugs": 8, "Atletico keychains": 5}},
  ],
  "PSG": [
    {"stock": {"PSG scarves": 30, "PSG jerseys": 25}, "prices": {"PSG scarves": 15, "PSG jerseys": 85}},
    {"stock": {"PSG hats": 35, "PSG flags": 20}, "prices": {"PSG hats": 12, "PSG flags": 10}},
    {"stock": {"PSG mugs": 25, "PSG keychains": 60}, "prices": {"PSG mugs": 8, "PSG keychains": 5}},
  ]
}

def get_finals_merch(team1_name, team2_name):
  merch = []
  if team1_name in FINALS_MERCH_TEMPLATE:
    merch.extend(FINALS_MERCH_TEMPLATE[team1_name])
  if team2_name in FINALS_MERCH_TEMPLATE:
    merch.extend(FINALS_MERCH_TEMPLATE[team2_name])
  return merch