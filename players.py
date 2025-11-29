PROB_FOUL_DEF = "PROB_FOUL_DEF"
PROB_FOUL_MID = "PROB_FOUL_MID"
PROB_STEAL_DEF_BY_FWD = "PROB_STEAL_DEF_BY_FWD"
PROB_STEAL_MID_BY_MID = "PROB_STEAL_MID_BY_MID"
PROB_STEAL_FWD_BY_DEF_OR_GK = "PROB_STEAL_FWD_BY_DEF_OR_GK"
PROB_SHOT_FWD = "PROB_SHOT_FWD"
PROB_SAVE_BY_GK = "PROB_SAVE_BY_GK"
PROB_SHOT_ON_TARGET = "PROB_SHOT_ON_TARGET"

TEAM_BARCA_PLAYERS = {
    "Marc-André ter Stegen": {"pos": "GK", "probs": {PROB_SAVE_BY_GK: 0.60}},
    # DEF
    "Jules Koundé":          {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.23}},
    "Ronald Araújo":         {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.27}},
    "Andreas Christensen":   {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.22}},
    "Alejandro Balde":       {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.21}},
    # MID
    "Frenkie de Jong":       {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.18}},
    "Pedri":                 {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.17}},
    "Ilkay Gündogan":        {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.16}},
    # FWD
    "Lamine Yamal":          {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.30, PROB_SHOT_FWD: 0.50, PROB_SHOT_ON_TARGET: 0.60}},
    "Robert Lewandowski":    {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.30, PROB_SHOT_FWD: 0.50, PROB_SHOT_ON_TARGET: 0.60}},
    "Raphinha":              {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.27, PROB_SHOT_FWD: 0.34, PROB_SHOT_ON_TARGET: 0.56}},
}

TEAM_REAL_PLAYERS = {
    "Thibaut Courtois":  {"pos": "GK",  "probs": {PROB_SAVE_BY_GK: 0.62}},
    # DEF
    "Dani Carvajal":     {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.22}},
    "Antonio Rüdiger":   {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.24}},
    "Éder Militão":      {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.25}},
    "Ferland Mendy":     {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.23}},
    # MID
    "Federico Valverde": {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.17}},
    "Aurélien Tchouaméni":{"pos": "MID","probs": {PROB_STEAL_MID_BY_MID: 0.19}},
    "Eduardo Camavinga": {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.18}},
    "Jude Bellingham":   {"pos": "MID", "probs": {PROB_SHOT_FWD: 0.46, PROB_SHOT_ON_TARGET: 0.58}},
    # FWD
    "Vinícius Júnior":   {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.29, PROB_SHOT_FWD: 0.48, PROB_SHOT_ON_TARGET: 0.58}},
    "Rodrygo":           {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.27, PROB_SHOT_FWD: 0.46, PROB_SHOT_ON_TARGET: 0.57}},
}



TEAM_ATLETICO_PLAYERS = {
    "Jan Oblak":           {"pos": "GK",  "probs": {PROB_SAVE_BY_GK: 0.61}},
    # DEF
    "José María Giménez":  {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.25}},
    "Stefan Savić":        {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.23}},
    "Mario Hermoso":       {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.22}},
    "Nahuel Molina":       {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.21}},
    # MID
    "Koke":                {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.17}},
    "Rodrigo De Paul":     {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.18}},
    "Saúl Ñíguez":         {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.16}},
    # FWD
    "Antoine Griezmann":   {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.28, PROB_SHOT_FWD: 0.47, PROB_SHOT_ON_TARGET: 0.57}},
    "Álvaro Morata":       {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.26, PROB_SHOT_FWD: 0.45, PROB_SHOT_ON_TARGET: 0.55}},
    "Ángel Correa":        {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.25, PROB_SHOT_FWD: 0.42, PROB_SHOT_ON_TARGET: 0.56}},
}

TEAM_PSG_PLAYERS = {
    "Gianluigi Donnarumma": {"pos": "GK",  "probs": {PROB_SAVE_BY_GK: 0.60}},
    # DEF
    "Achraf Hakimi":        {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.21}},
    "Marquinhos":           {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.24}},
    "Milan Škriniar":       {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.23}},
    "Nuno Mendes":          {"pos": "DEF", "probs": {PROB_STEAL_FWD_BY_DEF_OR_GK: 0.22}},
    # MID
    "Vitinha":              {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.17}},
    "Warren Zaïre-Emery":   {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.18}},
    "Manuel Ugarte":        {"pos": "MID", "probs": {PROB_STEAL_MID_BY_MID: 0.19}},
    # FWD
    "Kylian Mbappé":        {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.30, PROB_SHOT_FWD: 0.52, PROB_SHOT_ON_TARGET: 0.62}},
    "Ousmane Dembélé":      {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.27, PROB_SHOT_FWD: 0.44, PROB_SHOT_ON_TARGET: 0.56}},
    "Randal Kolo Muani":    {"pos": "FWD", "probs": {PROB_STEAL_DEF_BY_FWD: 0.26, PROB_SHOT_FWD: 0.45, PROB_SHOT_ON_TARGET: 0.57}},
}