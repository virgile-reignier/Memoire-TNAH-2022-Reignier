import spacy
from spacy.kb import KnowledgeBase
from spacy.util import minibatch, compounding

import os
import csv
import random
import pickle
from pathlib import Path
from collections import Counter

input_dir = Path.cwd().parent / "input"
output_dir = Path.cwd().parent / "output"

nlp = spacy.load("/home/reignier/Bureau/Entity-linking/spacy-ner-irht-teklia/multi-home-c3po4-LOC-model-best")
nlp.add_pipe(nlp.create_pipe('sentencizer'))

def load_entities():
    """ Helper function to read in the pre-defined entities we want to disambiguate to. """
    entities_loc = input_dir / "kb_Vienne.csv"
    alias_loc = input_dir / "alias.csv"

    names = dict()
    descriptions = dict()
    with entities_loc.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        for row in csvreader:
            qid = row[0]
            name = row[1]
            desc = row[15]
            names[qid] = name
            descriptions[qid] = desc

    with alias_loc.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        aliases = {}
        for row in csvreader:
            name = row[0]
            qid = row[1]
            if name not in aliases:
                aliases[name] = [[qid], [1]]
            else:
                aliases[name][0].append(qid)
                aliases[name][1] = [1/len(aliases[name][0]) for qid in aliases[name][0]]
    return names, descriptions, aliases


def create_kb():
    name_dict, desc_dict, aliases = load_entities()

    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=0)

    for qid, desc in desc_dict.items():
        desc_doc = nlp(desc)
        desc_enc = desc_doc.vector
        kb.add_entity(entity=qid, entity_vector=desc_enc, freq=342)

    for name, prob in aliases.items():
        kb.add_alias(alias=name, entities=prob[0], probabilities=prob[1])

    print()
    print(f"Entities in the KB: {kb.get_entity_strings()}")
    print(f"Aliases in the KB: {kb.get_alias_strings()}")
    print(f"candidates for francorum: {[c.entity_ for c in kb.get_candidates('francorum')]}")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    kb.dump(output_dir / "my_kb")
    nlp.to_disk(output_dir / "my_nlp")


def train_el():
    """ Step 2: Once we have done the manual annotations, use it to train a new Entity Linking component. """

    # data_for_trail = input_dir / "extrait_entites_arkindex.csv"
    data_for_trail = input_dir / "entites_vienne.csv"

    nlp = spacy.load(output_dir / "my_nlp")
    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=1)
    kb.load_bulk(output_dir / "my_kb")

    dataset = []
    with data_for_trail.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        for row in csvreader:
            text = row[0]
            offset = (int(row[3]), int(row[3]) + int(row[4]))
            # print(text[offset[0]:offset[1]])
            qid = row[7]
            #dataset.append((text, {"links": {offset: {qid: 1.0}}}))
            dataset.append(("", {"links": {(0, 0): {"": 1.0}}}))

    gold_ids = []
    for text, annot in dataset:
        for span, links_dict in annot["links"].items():
            for link, value in links_dict.items():
                if value:
                    gold_ids.append(link)

    print()
    print("Statistics of manually annotated data:")
    print(Counter(gold_ids))
    print()

    train_dataset = []
    test_dataset = []
    for QID in ['96970', '101949']:
        indices = [i for i,j in enumerate(gold_ids) if j == QID]
        train_dataset.extend(dataset[index] for index in indices[0:8])  # first 8 in training
        test_dataset.extend(dataset[index] for index in indices[8:10])  # last 2 in test

    # avoid artificial signals by reshuffling the datasets
    random.shuffle(train_dataset)
    random.shuffle(test_dataset)

    TRAIN_DOCS = []
    for text, annotation in train_dataset:
        doc = nlp(text)   # to make this more efficient, you can use nlp.pipe() just once for all the texts
        TRAIN_DOCS.append((doc, annotation))

    entity_linker = nlp.create_pipe("entity_linker", config={"incl_prior": False})
    entity_linker.set_kb(kb)
    nlp.add_pipe(entity_linker, last=True)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    print("Training the entity linker")
    with nlp.disable_pipes(*other_pipes):   # train only the entity_linker
        optimizer = nlp.begin_training()
        for itn in range(500):   # 500 iterations takes about a minute to train on this small dataset
            random.shuffle(TRAIN_DOCS)
            batches = minibatch(TRAIN_DOCS, size=compounding(4.0, 32.0, 1.001))   # increasing batch size
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,
                    annotations,
                    drop=0.2,   # prevent overfitting
                    losses=losses,
                    sgd=optimizer,
                )
            if itn % 50 == 0:
                print(itn, "Losses", losses)   # print the training loss
    print(itn, "Losses", losses)
    print()

    nlp.to_disk(output_dir / "my_nlp_el")

    with open(output_dir / "test_set.pkl", "wb") as f:
        pickle.dump(test_dataset, f)


def eval():
    """ Step 3: Evaluate the new Entity Linking component by applying it to unseen text. """
    nlp = spacy.load(output_dir / "my_nlp_el")
    with open(output_dir / "test_set.pkl", "rb") as f:
        test_dataset = pickle.load(f)

    data_for_trail = input_dir / "extrait_français_france.csv"

    with data_for_trail.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="\t")
        for row in csvreader:
            text = row[0]

            doc = nlp(text)
            for ent in doc.ents:
                print(ent.text, ent.label_, ent.kb_id_)
            print()

    for text, true_annot in test_dataset:
        print(text)
        print(f"Gold annotation: {true_annot}")
        doc = nlp(text)   # to make this more efficient, you can use nlp.pipe() just once for all the texts
        for ent in doc.ents:
            print(f"Prediction: {ent.text}, {ent.label_}, {ent.kb_id_}")
        print()


if __name__ == "__main__":
    create_kb()
    train_el()
    eval()