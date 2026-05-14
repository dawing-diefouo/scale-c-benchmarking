---
dataset_info:
  - config_name: argument_mining
    features:
      - name: text
        dtype: string
      - name: labels
        dtype:
          sequence:
            class_label:
              names:
                "0": mpos
                "1": premise
                "2": non-arg
    splits:
      - name: train
        num_bytes: 1426507
        num_examples: 12451
      - name: test
        num_bytes: 411338
        num_examples: 3571
      - name: validation
        num_bytes: 206802
        num_examples: 1786
  - config_name: db_aspect
    features:
      - name: text
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": Allgemein:negative
              "1": Allgemein:neutral
              "2": Allgemein:positive
              "3": Atmosphäre:negative
              "4": Atmosphäre:neutral
              "5": Atmosphäre:positive
              "6": Auslastung_und_Platzangebot:negative
              "7": Auslastung_und_Platzangebot:neutral
              "8": Auslastung_und_Platzangebot:positive
              "9": Barrierefreiheit:negative
              "10": Barrierefreiheit:neutral
              "11": Barrierefreiheit:positive
              "12": Connectivity:negative
              "13": Connectivity:neutral
              "14": Connectivity:positive
              "15": DB_App_und_Website:negative
              "16": DB_App_und_Website:neutral
              "17": DB_App_und_Website:positive
              "18": Design:negative
              "19": Design:neutral
              "20": Design:positive
              "21": Gastronomisches_Angebot:negative
              "22": Gastronomisches_Angebot:neutral
              "23": Gastronomisches_Angebot:positive
              "24": Gepäck:negative
              "25": Gepäck:neutral
              "26": Image:negative
              "27": Image:neutral
              "28": Image:positive
              "29": Informationen:negative
              "30": Informationen:neutral
              "31": Informationen:positive
              "32": Komfort_und_Ausstattung:negative
              "33": Komfort_und_Ausstattung:neutral
              "34": Komfort_und_Ausstattung:positive
              "35": QR-Code:negative
              "36": QR-Code:neutral
              "37": QR-Code:positive
              "38": Reisen_mit_Kindern:negative
              "39": Reisen_mit_Kindern:neutral
              "40": Reisen_mit_Kindern:positive
              "41": Service_und_Kundenbetreuung:negative
              "42": Service_und_Kundenbetreuung:neutral
              "43": Service_und_Kundenbetreuung:positive
              "44": Sicherheit:negative
              "45": Sicherheit:neutral
              "46": Sicherheit:positive
              "47": Sonstige_Unregelmässigkeiten:negative
              "48": Sonstige_Unregelmässigkeiten:neutral
              "49": Sonstige_Unregelmässigkeiten:positive
              "50": Ticketkauf:negative
              "51": Ticketkauf:neutral
              "52": Ticketkauf:positive
              "53": Ticketkauf:positve
              "54": Toiletten:negative
              "55": Toiletten:neutral
              "56": Toiletten:positive
              "57": Zugfahrt:negative
              "58": Zugfahrt:neutral
              "59": Zugfahrt:positive
    splits:
      - name: train
        num_bytes: 3582769
        num_examples: 16200
      - name: test
        num_bytes: 827563
        num_examples: 2095
      - name: validation
        num_bytes: 419520
        num_examples: 1930
  - config_name: engaging_comments
    features:
      - name: text
        dtype: string
      - name: labels
        dtype: uint64
    splits:
      - name: train
        num_bytes: 586426
        num_examples: 2920
      - name: test
        num_bytes: 203991
        num_examples: 944
      - name: validation
        num_bytes: 59372
        num_examples: 324
  - config_name: factclaiming_comments
    features:
      - name: text
        dtype: string
      - name: labels
        dtype: uint64
    splits:
      - name: train
        num_bytes: 586426
        num_examples: 2920
      - name: test
        num_bytes: 203991
        num_examples: 944
      - name: validation
        num_bytes: 59372
        num_examples: 324
  - config_name: germanquad
    features:
      - name: id
        dtype: string
      - name: context
        dtype: string
      - name: question
        dtype: string
      - name: answers
        sequence:
          - name: text
            dtype: string
          - name: answer_start
            dtype: int32
    splits:
      - name: train
        num_bytes: 18032041
        num_examples: 11518
      - name: test
        num_bytes: 6443430
        num_examples: 2204
  - config_name: germeval_opinions
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            class_label:
              names:
                "0": "O"
                "1": "B-OPINION"
                "2": "I-OPINION"
                "3": ""
    splits:
      - name: train
        num_bytes: 10880134
        num_examples: 19432
      - name: test
        num_bytes: 3136657
        num_examples: 2566
      - name: validation
        num_bytes: 1306168
        num_examples: 2369
  - config_name: hotel_aspect
    features:
      - name: text
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": ESSEN&TRINKEN:negativ
              "1": ESSEN&TRINKEN:neutral
              "2": ESSEN&TRINKEN:positiv
              "3": HOTEL:negativ
              "4": HOTEL:neutral
              "5": HOTEL:positiv
              "6": LAGE:negativ
              "7": LAGE:neutral
              "8": LAGE:positiv
              "9": SERVICE:negativ
              "10": SERVICE:neutral
              "11": SERVICE:positiv
              "12": ZIMMER:negativ
              "13": ZIMMER:neutral
              "14": ZIMMER:positiv
    splits:
      - name: train
        num_bytes: 299910
        num_examples: 2977
      - name: test
        num_bytes: 87559
        num_examples: 851
      - name: validation
        num_bytes: 46016
        num_examples: 426
  - config_name: massive_intents
    features:
      - name: text
        dtype: string
      - name: labels
        dtype: uint64
    splits:
      - name: train
        num_bytes: 696901
        num_examples: 13382
      - name: test
        num_bytes: 86052
        num_examples: 1652
      - name: validation
        num_bytes: 76949
        num_examples: 1487
  - config_name: massive_seq
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            class_label:
              names:
                "0": "-"
                "1": date
                "2": time
                "3": house_place
                "4": change_amount
                "5": artist_name
                "6": media_type
                "7": place_name
                "8": time_zone
                "9": order_type
                "10": food_type
                "11": news_topic
                "12": song_name
                "13": music_genre
                "14": device_type
                "15": meal_type
                "16": business_name
                "17": general_frequency
                "18": weather_descriptor
                "19": player_setting
                "20": joke_type
                "21": color_type
                "22": event_name
                "23": timeofday
                "24": business_type
                "25": music_descriptor
                "26": playlist_name
                "27": person
                "28": alarm_type
                "29": app_name
                "30": coffee_type
                "31": relation
                "32": movie_name
                "33": drink_type
                "34": transport_type
                "35": music_album
                "36": list_name
                "37": sport_type
                "38": radio_name
                "39": podcast_name
                "40": audiobook_name
                "41": audiobook_author
                "42": cooking_type
                "43": ingredient
                "44": game_name
                "45": podcast_descriptor
                "46": movie_type
                "47": personal_info
                "48": transport_agency
                "49": transport_name
                "50": transport_descriptor
                "51": currency_name
                "52": definition_word
                "53": game_type
                "54": email_address
                "55": email_folder
    splits:
      - name: train
        num_bytes: 696901
        num_examples: 13382
      - name: test
        num_bytes: 86052
        num_examples: 1652
      - name: validation
        num_bytes: 76949
        num_examples: 1487
  - config_name: mlqa
    features:
      - name: id
        dtype: string
      - name: context
        dtype: string
      - name: question
        dtype: string
      - name: answers
        sequence:
          - name: text
            dtype: string
          - name: answer_start
            dtype: int32
    splits:
      - name: train
        num_bytes: 476830
        num_examples: 512
      - name: test
        num_bytes: 4269952
        num_examples: 4517
  - config_name: ner_biofid
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            class_label:
              names:
                "0": O
                "1": B-TME
                "2": B-LOC
                "3": B-TAX
                "4": B-OTHER
                "5": I-OTHER
                "6": ""
                "7": I-TAX
                "8": I-LOC
                "9": B-ORG
                "10": I-ORG
                "11": B-PER
                "12": I-PER
                "13": I-TME
    splits:
      - name: train
        num_bytes: 5280623
        num_examples: 12668
      - name: test
        num_bytes: 672243
        num_examples: 1584
      - name: validation
        num_bytes: 484834
        num_examples: 1584
  - config_name: ner_europarl
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            class_label:
              names:
                "0": O
                "1": I-MISC
                "2": I-ORG
                "3": I-PER
                "4": I-LOC
    splits:
      - name: train
        num_bytes: 1438570
        num_examples: 3184
      - name: test
        num_bytes: 372681
        num_examples: 858
      - name: validation
        num_bytes: 165981
        num_examples: 354
  - config_name: ner_legal
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            class_label:
              names:
                "0": O
                "1": B-GS
                "2": I-GS
                "3": B-RS
                "4": I-RS
                "5": B-GRT
                "6": I-GRT
                "7": B-LIT
                "8": I-LIT
                "9": B-VS
                "10": I-VS
                "11": B-ORG
                "12": B-VT
                "13": I-VT
                "14": B-INN
                "15": I-INN
                "16": B-MRK
                "17": B-EUN
                "18": I-EUN
                "19": B-RR
                "20": B-UN
                "21": B-PER
                "22": B-ST
                "23": I-UN
                "24": B-VO
                "25": I-VO
                "26": B-LD
                "27": I-PER
                "28": I-MRK
                "29": I-ORG
                "30": I-LD
                "31": B-AN
                "32": I-ST
                "33": I-AN
                "34": B-STR
                "35": I-STR
                "36": B-LDS
                "37": I-RR
                "38": I-LDS
    splits:
      - name: train
        num_bytes: 30338349
        num_examples: 53384
      - name: test
        num_bytes: 3851182
        num_examples: 6673
      - name: validation
        num_bytes: 3811829
        num_examples: 6666
  - config_name: ner_wiki_news
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            class_label:
              names:
                "0": B-PER
                "1": O
                "2": B-ORG
                "3": I-PER
                "4": B-LOC
                "5": I-ORG
                "6": B-LOCderiv
                "7": B-ORGpart
                "8": B-OTH
                "9": I-OTH
                "10": I-LOCderiv
                "11": B-PERpart
                "12": I-ORGpart
                "13": B-LOCpart
                "14": I-LOC
                "15": B-OTHderiv
                "16": B-PERderiv
                "17": B-OTHpart
                "18": I-OTHpart
                "19": I-OTHderiv
                "20": B-ORGderiv
                "21": I-PERpart
                "22": I-LOCpart
                "23": I-PERderiv
                "24": I-ORGderiv
    splits:
      - name: train
        num_bytes: 8092200
        num_examples: 24000
      - name: test
        num_bytes: 1723799
        num_examples: 5100
      - name: validation
        num_bytes: 742609
        num_examples: 2200
  - config_name: ner_news
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            class_label:
              names:
                "0": O
                "1": I-LOC
                "2": I-ORG
                "3": I-MISC
                "4": I-PER
                "5": B-MISC
                "6": B-LOC
                "7": B-PER
    splits:
      - name: train
        num_bytes: 820868
        num_examples: 2587
      - name: test
        num_bytes: 922729
        num_examples: 3007
      - name: validation
        num_bytes: 97087
        num_examples: 287
  - config_name: news_class
    features:
      - name: title
        dtype: string
      - name: text
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": finance
              "1": entertainment
              "2": sports
              "3": news
              "4": autos
              "5": video
              "6": lifestyle
              "7": travel
              "8": health
              "9": foodanddrink
    splits:
      - name: train
        num_bytes: 24001478
        num_examples: 9000
      - name: test
        num_bytes: 26631151
        num_examples: 10000
      - name: validation
        num_bytes: 2755997
        num_examples: 1000
  - config_name: nli
    features:
      - name: sentence_1
        dtype: string
      - name: sentence_2
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": contradiction
              "1": entailment
              "2": neutral
    splits:
      - name: train
        num_bytes: 446460
        num_examples: 2245
      - name: test
        num_bytes: 996488
        num_examples: 5010
      - name: validation
        num_bytes: 48951
        num_examples: 250
  - config_name: offensive_lang
    features:
      - name: text
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": OTHER
              "1": INSULT
              "2": PROFANITY
              "3": ABUSE
    splits:
      - name: train
        num_bytes: 709308
        num_examples: 4508
      - name: test
        num_bytes: 480934
        num_examples: 3398
      - name: validation
        num_bytes: 76666
        num_examples: 501
  - config_name: paraphrase_matching
    features:
      - name: sentence_1
        dtype: string
      - name: sentence_2
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": 0
              "1": 1
    splits:
      - name: train
        num_bytes: 12610356
        num_examples: 49401
      - name: test
        num_bytes: 516456
        num_examples: 2000
      - name: validation
        num_bytes: 506251
        num_examples: 2000
  - config_name: pawsx
    features:
      - name: sentence_1
        dtype: string
      - name: sentence_2
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": 0
              "1": 1
    splits:
      - name: train
        num_bytes: 12610356
        num_examples: 49401
      - name: test
        num_bytes: 516456
        num_examples: 2000
      - name: validation
        num_bytes: 506251
        num_examples: 2000
  - config_name: polarity
    features:
      - name: text
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": neutral
              "1": positive
              "2": negative
    splits:
      - name: train
        num_bytes: 10698974
        num_examples: 20941
      - name: test
        num_bytes: 1301161
        num_examples: 2566
      - name: validation
        num_bytes: 1407114
        num_examples: 2584
  - config_name: query_ad
    features:
      - name: sentence_1
        dtype: string
      - name: sentence_2
        dtype: string
      - name: sentence_3
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": Good
              "1": Bad
    splits:
      - name: train
        num_bytes: 1409398
        num_examples: 9000
      - name: test
        num_bytes: 1563969
        num_examples: 10000
      - name: validation
        num_bytes: 156599
        num_examples: 1000
  - config_name: quest_ans
    features:
      - name: sentence_1
        dtype: string
      - name: sentence_2
        dtype: string
      - name: sentence_3
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": 0
              "1": 1
    splits:
      - name: train
        num_bytes: 3011127
        num_examples: 8972
      - name: test
        num_bytes: 3350726
        num_examples: 9921
      - name: validation
        num_bytes: 334876
        num_examples: 1000
  - config_name: topic_relevance
    features:
      - name: text
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": "true"
              "1": "false"
    splits:
      - name: train
        num_bytes: 10698974
        num_examples: 20941
      - name: test
        num_bytes: 1301161
        num_examples: 2566
      - name: validation
        num_bytes: 1407114
        num_examples: 2584
  - config_name: toxic_comments
    features:
      - name: text
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": 0
              "1": 1
    splits:
      - name: train
        num_bytes: 595186
        num_examples: 2920
      - name: test
        num_bytes: 206823
        num_examples: 944
      - name: validation
        num_bytes: 60344
        num_examples: 324
  - config_name: up_dep
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            dtype:
              class_label:
                names:
                  "0": advmod
                  "1": amod
                  "2": root
                  "3": punct
                  "4": conj
                  "5": det
                  "6": nmod
                  "7": parataxis
                  "8": nsubj
                  "9": iobj
                  "10": dobj
                  "11": compound:prt
                  "12": nsubjpass
                  "13": _
                  "14": case
                  "15": name
                  "16": appos
                  "17": cc
                  "18": aux
                  "19": cop
                  "20": neg
                  "21": mark
                  "22": acl
                  "23": advcl
                  "24": auxpass
                  "25": nummod
                  "26": det:poss
                  "27": xcomp
                  "28": dep
                  "29": ccomp
                  "30": compound
                  "31": csubj
                  "32": expl
                  "33": mwe
                  "34": csubjpass
                  "35": nmod:poss
    splits:
      - name: train
        num_bytes: 4846455
        num_examples: 14118
      - name: test
        num_bytes: 292472
        num_examples: 977
      - name: validation
        num_bytes: 219953
        num_examples: 799
  - config_name: up_pos
    features:
      - name: tokens
        dtype:
          sequence:
            dtype: string
      - name: tags
        dtype:
          sequence:
            dtype:
              class_label:
                names:
                  "0": ADV
                  "1": ADJ
                  "2": NOUN
                  "3": PUNCT
                  "4": DET
                  "5": VERB
                  "6": PRON
                  "7": ADP
                  "8": _
                  "9": PROPN
                  "10": CONJ
                  "11": AUX
                  "12": PART
                  "13": SCONJ
                  "14": NUM
                  "15": X
    splits:
      - name: train
        num_bytes: 4846455
        num_examples: 14118
      - name: test
        num_bytes: 292472
        num_examples: 977
      - name: validation
        num_bytes: 219953
        num_examples: 799
  - config_name: verbal_idioms
    features:
      - name: sentence_1
        dtype: string
      - name: sentence_2
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": literally
              "1": figuratively
              "2": undecidable
              "3": both
    splits:
      - name: train
        num_bytes: 3159615
        num_examples: 6676
      - name: test
        num_bytes: 675805
        num_examples: 1455
      - name: validation
        num_bytes: 668883
        num_examples: 1448
  - config_name: webcage
    features:
      - name: sentence_1
        dtype: string
      - name: sentence_2
        dtype: string
      - name: sentence_3
        dtype: string
      - name: labels
        dtype:
          class_label:
            names:
              "0": True
              "1": False
    splits:
      - name: train
        num_bytes: 1109888
        num_examples: 6249
      - name: test
        num_bytes: 380957
        num_examples: 2008
      - name: validation
        num_bytes: 183427
        num_examples: 1032
configs:
  - config_name: argument_mining
    data_files:
      - split: train
        path: argument_mining/train-*
      - split: test
        path: argument_mining/test-*
      - split: validation
        path: argument_mining/validation-*
  - config_name: db_aspect
    data_files:
      - split: train
        path: db_aspect/train-*
      - split: test
        path: db_aspect/test-*
      - split: validation
        path: db_aspect/validation-*
  - config_name: engaging_comments
    data_files:
      - split: train
        path: engaging_comments/train-*
      - split: test
        path: engaging_comments/test-*
      - split: validation
        path: engaging_comments/validation-*
  - config_name: factclaiming_comments
    data_files:
      - split: train
        path: factclaiming_comments/train-*
      - split: test
        path: factclaiming_comments/test-*
      - split: validation
        path: factclaiming_comments/validation-*
  - config_name: germanquad
    data_files:
      - split: train
        path: germanquad/train-*
      - split: test
        path: germanquad/test-*
  - config_name: germeval_opinions
    data_files:
      - split: train
        path: germeval_opinions/train-*
      - split: test
        path: germeval_opinions/test-*
      - split: validation
        path: germeval_opinions/validation-*
  - config_name: hotel_aspect
    data_files:
      - split: train
        path: hotel_aspect/train-*
      - split: test
        path: hotel_aspect/test-*
      - split: validation
        path: hotel_aspect/validation-*
  - config_name: massive_intents
    data_files:
      - split: train
        path: massive_intents/train-*
      - split: test
        path: massive_intents/test-*
      - split: validation
        path: massive_intents/validation-*
  - config_name: massive_seq
    data_files:
      - split: train
        path: massive_seq/train-*
      - split: test
        path: massive_seq/test-*
      - split: validation
        path: massive_seq/validation-*
  - config_name: mlqa
    data_files:
      - split: test
        path: mlqa/test-*
      - split: train
        path: mlqa/validation-*
  - config_name: ner_biofid
    data_files:
      - split: train
        path: ner_biofid/train-*
      - split: test
        path: ner_biofid/test-*
      - split: validation
        path: ner_biofid/validation-*
  - config_name: ner_europarl
    data_files:
      - split: train
        path: ner_europarl/train-*
      - split: test
        path: ner_europarl/test-*
      - split: validation
        path: ner_europarl/validation-*
  - config_name: ner_legal
    data_files:
      - split: train
        path: ner_legal/train-*
      - split: test
        path: ner_legal/test-*
      - split: validation
        path: ner_legal/validation-*
  - config_name: ner_wiki_news
    data_files:
      - split: train
        path: ner_wiki_news/train-*
      - split: test
        path: ner_wiki_news/test-*
      - split: validation
        path: ner_wiki_news/validation-*
  - config_name: ner_news
    data_files:
      - split: train
        path: ner_news/train-*
      - split: test
        path: ner_news/test-*
      - split: validation
        path: ner_news/validation-*
  - config_name: news_class
    data_files:
      - split: train
        path: news_class/train-*
      - split: test
        path: news_class/test-*
      - split: validation
        path: news_class/validation-*
  - config_name: nli
    data_files:
      - split: train
        path: nli/train-*
      - split: test
        path: nli/test-*
      - split: validation
        path: nli/validation-*
  - config_name: offensive_lang
    data_files:
      - split: train
        path: offensive_lang/train-*
      - split: test
        path: offensive_lang/test-*
      - split: validation
        path: offensive_lang/validation-*
  - config_name: paraphrase_matching
    data_files:
      - split: train
        path: pawsx/train-*
      - split: test
        path: pawsx/test-*
      - split: validation
        path: pawsx/validation-*
  - config_name: pawsx
    data_files:
      - split: train
        path: pawsx/train-*
      - split: test
        path: pawsx/test-*
      - split: validation
        path: pawsx/validation-*
  - config_name: polarity
    data_files:
      - split: train
        path: polarity/train-*
      - split: test
        path: polarity/test-*
      - split: validation
        path: polarity/validation-*
  - config_name: query_ad
    data_files:
      - split: train
        path: query_ad/train-*
      - split: test
        path: query_ad/test-*
      - split: validation
        path: query_ad/validation-*
  - config_name: quest_ans
    data_files:
      - split: train
        path: quest_ans/train-*
      - split: test
        path: quest_ans/test-*
      - split: validation
        path: quest_ans/validation-*
  - config_name: topic_relevance
    data_files:
      - split: train
        path: topic_relevance/train-*
      - split: test
        path: topic_relevance/test-*
      - split: validation
        path: topic_relevance/validation-*
  - config_name: toxic_comments
    data_files:
      - split: train
        path: toxic_comments/train-*
      - split: test
        path: toxic_comments/test-*
      - split: validation
        path: toxic_comments/validation-*
  - config_name: up_dep
    data_files:
      - split: train
        path: up_dep/train-*
      - split: test
        path: up_dep/test-*
      - split: validation
        path: up_dep/validation-*
  - config_name: up_pos
    data_files:
      - split: train
        path: up_pos/train-*
      - split: test
        path: up_pos/test-*
      - split: validation
        path: up_pos/validation-*
  - config_name: verbal_idioms
    data_files:
      - split: train
        path: verbal_idioms/train-*
      - split: test
        path: verbal_idioms/test-*
      - split: validation
        path: verbal_idioms/validation-*
  - config_name: webcage
    data_files:
      - split: train
        path: webcage/train-*
      - split: test
        path: webcage/test-*
      - split: validation
        path: webcage/validation-*
---

# SuperGLEBer
