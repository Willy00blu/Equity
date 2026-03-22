POSITIONS_MAP = {
    "UTG": "EP", "EP": "EP",
    "MP": "MP", "HJ": "MP", "HIGHJACK": "MP",
    "CO": "CO", "CUTOFF": "CO",
    "BTN": "BTN", "BU": "BTN", "BUTTON": "BTN",
    "SB": "SB", "SMALLBLIND": "SB",
    "BB": "BB", "BIGBLIND": "BB"
}

OPEN_RANGES = {
    "EP": {
        "always": {
            "AA","KK","QQ","JJ","TT","99","88","77",
            "AKs","AQs","AJs","ATs","A9s","A8s","A7s","A6s","A5s","A4s","A3s","A2s",
            "KQs","KJs","KTs","K9s","K8s","K7s",
            "QJs","QTs","Q9s",
            "JTs","T9s",
            "AKo","AQo","KQo","AJo"
        },
        "conditional": {"K6s","K5s","ATo","KJo","66"},
        "tip": "Apri queste solo se il BB è un giocatore scarso."
    },

    "MP": {
        "always": {
            "AA","KK","QQ","JJ","TT","99","88","77","66",
            "AKs","AQs","AJs","ATs","A9s","A8s","A7s","A6s","A5s","A4s","A3s","A2s",
            "KQs","KJs","KTs","K9s","K8s","K7s","K6s",
            "QJs","QTs","Q9s","Q8s",
            "JTs","J9s",
            "T9s",
            "AKo","KQo","QJo","AJo","KJo","ATo","KTo"
        },
        "conditional": {
            "A9o",
            "QTo",
            "K5s","K4s",
            "55"
        },
        "tip": "Apri queste solo se il BB è scarso."
    },

    "CO": {
        "always": {
            "AA","KK","QQ","JJ","TT","99","88","77","66","55","44",
            "AKs","AQs","AJs","ATs","A9s","A8s","A7s","A6s","A5s","A4s","A3s","A2s",
            "KQs","KJs","KTs","K9s","K8s","K7s","K6s","K5s","K4s",
            "QJs","QTs","Q9s","Q8s",
            "JTs","J9s","J8s",
            "T9s","T8s",
            "98s","87s","76s",
            "AKo","AQo","AJo","ATo","A9o","A8o",
            "KQo","KJo","QJo",
            "KTo","QTo","JTo"
        },
        "conditional": {
            "33",
            "A5o",
            "Q7s","Q6s",
            "J7s",
            "K3s","K2s",
            "65s","54s"
        },
        "tip": "Apri queste solo se il BTN è molto chiuso o il BB è scarso."
    },

    "BTN": {
        "always": {
            "AA","KK","QQ","JJ","TT","99","88","77","66","55","44","33","22",
            "AKs","AQs","AJs","ATs","A9s","A8s","A7s","A6s","A5s","A4s","A3s","A2s",
            "KQs","KJs","KTs","K9s","K8s","K7s","K6s","K5s","K4s","K3s","K2s",
            "QJs","QTs","Q9s","Q8s","Q7s","Q6s","Q5s","Q4s","Q3s",
            "JTs","J9s","J8s","J7s","J6s",
            "T9s","T8s","T7s","T6s",
            "98s","97s","96s",
            "87s","86s",
            "76s","75s",
            "65s",
            "54s",
            "AKo","AQo","AJo","ATo","A9o","A8o","A7o","A6o","A5o","A4o","A3o",
            "KQo","KJo","KTo","K9o","K8o",
            "QJo","QTo","Q9o",
            "JTo","J9o",
            "T9o"
        },
        "conditional": {
            "A2o",
            "K7o",
            "Q8o","Q2s",
            "J5s","J4s","J3s",
            "T8o","T5s",
            "98o",
            "85s",
            "74s",
            "64s",
            "53s"
        },
        "tip": "Apri queste solo se i bui sono passivi o scarsi."
    },

    "SB": {
        "always": {
            "AA","KK","QQ","JJ","TT","99","88","77","66","55","44","33","22",
            "AKs","AQs","AJs","ATs","A9s","A8s","A7s","A6s","A5s","A4s","A3s","A2s",
            "KQs","KJs","KTs","K9s","K8s","K7s","K6s","K5s","K4s","K3s","K2s",
            "QJs","QTs","Q9s","Q8s","Q7s","Q6s","Q5s","Q4s","Q3s","Q2s",
            "JTs","J9s","J8s","J7s","J6s","J5s",
            "T9s","T8s","T7s","T6s",
            "98s","97s","96s",
            "87s","86s",
            "76s","75s",
            "65s","64s",
            "54s",
            "AKo","AQo","AJo","ATo","A9o","A8o","A7o","A6o","A5o","A4o","A3o",
            "KQo","KJo","KTo","K9o","K8o",
            "QJo","QTo","Q9o",
            "JTo","J9o",
            "T9o","T8o",
            "98o"
        },
        "conditional": {
            "A2o",
            "K7o",
            "Q8o",
            "T5s",
            "J4s","J3s",
            "85s",
            "74s",
            "53s"
        },
        "tip": "Apri queste solo se il BB folda molto o è scarso."
    }
}
