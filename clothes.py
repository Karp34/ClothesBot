clothes = {
    "super_cold":{ #temp0 <= -20
        "jacket": "cold",
        "upper_wear": "sweater",
        "second_sweater": "cold",
        "t-shirt": "regular",
        "pants": "cold",
        "warm_pants": "cold",
        "socks": "regular",
        "warm_socks": "cold",
        "sneakers": "cold",
        "hat": "cold",
        "warm_gloves": "cold",
        "scarf": "cold"
    },
    "cold":{ #temp0 <= -5 and temp0 > -20
        "jacket": "cold",
        "upper_wear": "sweater",
        "second_sweater": False,
        "t-shirt": "regular",
        "pants": "regular",
        "warm_pants": "cold",
        "socks": "regular",
        "warm_socks": False,
        "sneakers": "cold",
        "hat": "cold",
        "warm_gloves": "cold"
    },
    "coldy":{ #temp0 <= 5 and temp0 > -5
        "jacket": "coldy",
        "upper_wear": "sweater",
        "second_sweater": False,
        "t-shirt": "regular",
        "pants": "regular",
        "warm_pants": False,
        "socks": "regular",
        "warm_socks": False,
        "sneakers": "regular",
        "hat": [
            "cold",
            False],
        "umbrella":[
            False,
            "regular"]
    },
    "regular":{  #temp0 <= 15 and temp0 > 5
        "jacket": [
          "regular",
          "regular",
          "regular",
          "regular"],
        "upper_wear": "sweater",
        "second_sweater": False,
        "t-shirt": "regular",
        "pants": "regular",
        "warm_pants": False,
        "socks": "regular",
        "warm_socks": False,
        "sneakers" : "regular",
        "hat": False,
        "sunglasses": False,
        "umbrella":[
            False,
            "regular",
            False,
            "regular"]
    },
    "warm":{ #temp0 <= 20 and temp0 > 15
        "jacket": False,
        "upper_wear": [
            "sweater",
            "sweater",
            False,
            "sweater"],
        "second_sweater": False,
        "t-shirt": "regular",
        "pants": "regular",
        "warm_pants": False,
        "socks": [
            "warm",
            "regular",
            "warm",
            "regular"],
        "warm_socks": False,
        "sneakers": [
            "warm",
            "regular",
            "warm"],
        "hat": False,
        "sunglasses": False,
        "umbrella":[
            False,
            "regular",
            False,
            "regular"]
    },
    "hot":{ # temp0 > 20
        "jacket": False,
        "upper_wear": [
            False,
            "shirt",
            False,
            False],
        "second_sweater": False,
        "t-shirt": [
            "regular",
            False,
            "regular",
            "regular"],
        "pants": [
            "hot",
            "regular",
            "hot",
            "hot"],
        "warm_pants": False,
        "socks": [
            "warm",
            "regular",
            "warm",
            "warm"],
        "warm_socks": False,
        "sneakers": "warm",
        "hat": False,
        "sunglasses": [
            False,
            "regular",
            False,
            False],
        "umbrella":[
            False,
            "regular",
            False,
            "regular"]
    },
}